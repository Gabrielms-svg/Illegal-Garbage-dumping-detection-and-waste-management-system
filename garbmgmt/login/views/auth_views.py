import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from ..models import (
    User,
    Normal_user,
    Authority_user,
    GarbageReport,
    DumpingEvent,
    LegalDumpingLocation,
)


def about(request):
    return render(request, 'about.html')


def home(request):
    events = DumpingEvent.objects.all().order_by('-timestamp')[:20]
    return render(request, 'home.html', {'events': events})


def user_register(request):
    if request.method == 'POST':
        profile = request.FILES.get('profile')
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('user_register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('user_register')

        User.objects.create_user(email=email, password=password2, first_name=fullname)
        Normal_user.objects.create(
            profile=profile,
            phone=phone,
            fullname=fullname,
            email=email,
            password=make_password(password2),
        )

    return render(request, 'user_register.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None and not user.is_staff:
            login(request, user)
            return redirect('user_dashboard')

        try:
            normal_profile = Normal_user.objects.get(email=email)
        except Normal_user.DoesNotExist:
            messages.error(request, 'Invalid login credentials')
            return redirect('user_login')

        if not check_password(password, normal_profile.password):
            messages.error(request, 'Invalid login credentials')
            return redirect('user_login')

        user, created = User.objects.get_or_create(
            email=normal_profile.email,
            defaults={'first_name': normal_profile.fullname},
        )

        if created or not user.has_usable_password():
            user.set_password(password)
            user.save()

        login(request, user)
        return redirect('user_dashboard')

    return render(request, 'user_login.html')


def auth_login(request):
    if request.method == 'POST':
        auth_id = request.POST.get('auth_id')
        password = request.POST.get('password')

        try:
            authority_profile = Authority_user.objects.get(auth_id=auth_id)
            if authority_profile.password != password:
                messages.error(request, 'Invalid password!')
                return redirect('auth_login')

            auth_user, created = User.objects.get_or_create(
                email=authority_profile.email,
                defaults={
                    'first_name': authority_profile.first_name,
                    'is_staff': True,
                }
            )
            if created:
                auth_user.set_password(password)
                auth_user.save()
            elif not auth_user.check_password(password):
                messages.error(request, 'Invalid password!')
                return redirect('auth_login')

            if not auth_user.is_staff:
                auth_user.is_staff = True
                auth_user.save()

            login(request, auth_user)
            messages.success(request, 'Authority Login Successful!')
            return redirect('auth_dashboard')
        except Authority_user.DoesNotExist:
            messages.error(request, 'Invalid Authority ID!')
            return redirect('auth_login')

    return render(request, 'auth_login.html')


@login_required(login_url='user_login')
def user_dashboard(request):
    try:
        profile = Normal_user.objects.get(email=request.user.email)
    except Normal_user.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('user_login')

    reports = GarbageReport.objects.filter(user=profile).order_by('-created_at')
    return render(request, 'user_dashboard.html', {'logged_user': profile, 'reports': reports})


def user_logout(request):
    logout(request)
    return redirect('user_login')


def auth_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


@login_required(login_url='auth_login')
def auth_dashboard(request):
    if not request.user.is_staff:
        return redirect('auth_login')

    reports = GarbageReport.objects.prefetch_related('evidences').order_by('-created_at')
    cctv_events = DumpingEvent.objects.all().order_by('-timestamp')
    current_time = now()

    total_reports_this_month = sum(
        1
        for r in reports
        if r.created_at.year == current_time.year and r.created_at.month == current_time.month
    )

    new_cctv_today = sum(
        1
        for e in cctv_events
        if e.timestamp.date() == current_time.date()
    )

    return render(
        request,
        'auth_dashboard.html',
        {
            'cctv_events': cctv_events,
            'reports': reports,
            'last_updated': current_time,
            'total_reports_this_month': total_reports_this_month,
            'new_cctv_today': new_cctv_today,
        },
    )


@login_required(login_url='auth_login')
def save_location(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        authority = Authority_user.objects.get(email=request.user.email)
    except Authority_user.DoesNotExist:
        return JsonResponse({'error': 'Authority profile not found'}, status=403)

    data = json.loads(request.body)
    LegalDumpingLocation.objects.create(
        name=data.get('name'),
        location_type=data.get('type'),
        latitude=data.get('lat'),
        longitude=data.get('lng'),
        added_by=authority,
    )

    return JsonResponse({'status': 'success'})


def get_locations(request):
    locations = LegalDumpingLocation.objects.filter(is_active=True)
    data = [
        {
            'id': loc.id,
            'name': loc.name,
            'type': loc.location_type,
            'lat': loc.latitude,
            'lng': loc.longitude,
        }
        for loc in locations
    ]
    return JsonResponse(data, safe=False)


@login_required(login_url='auth_login')
def delete_location(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'invalid'}, status=400)

    if not request.user.is_staff:
        return JsonResponse({'status': 'unauthorized'}, status=403)

    try:
        authority = Authority_user.objects.get(email=request.user.email)
    except Authority_user.DoesNotExist:
        return JsonResponse({'status': 'unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        location_id = data.get('id')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'invalid_json'}, status=400)

    location = get_object_or_404(
        LegalDumpingLocation,
        id=location_id,
        added_by=authority,
        is_active=True,
    )
    location.is_active = False
    location.save()

    return JsonResponse({'status': 'success'})
