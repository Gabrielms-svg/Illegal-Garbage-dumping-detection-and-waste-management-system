import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from ..models import (
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

        try:
            user = Normal_user.objects.get(email=email)
            if check_password(password, user.password):
                request.session['normal_user_id'] = user.id
                request.session['normal_user_name'] = user.fullname
                return redirect('user_dashboard')

            messages.error(request, 'Invalid password')
            return redirect('user_login')
        except Normal_user.DoesNotExist:
            messages.error(request, 'User not found')
            return redirect('user_login')

    return render(request, 'user_login.html')


def auth_login(request):
    if request.method == 'POST':
        auth_id = request.POST.get('auth_id')
        password = request.POST.get('password')

        try:
            user = Authority_user.objects.get(auth_id=auth_id)
            if user.password == password:
                request.session['authority_user_id'] = user.id
                request.session['authority_user_name'] = user.first_name
                messages.success(request, 'Authority Login Successful!')
                return redirect('auth_dashboard')

            messages.error(request, 'Invalid password!')
            return redirect('auth_login')
        except Authority_user.DoesNotExist:
            messages.error(request, 'Invalid Authority ID!')
            return redirect('auth_login')

    return render(request, 'auth_login.html')


def user_dashboard(request):
    if 'normal_user_id' not in request.session:
        return redirect('user_login')

    user = Normal_user.objects.get(id=request.session['normal_user_id'])
    reports = GarbageReport.objects.filter(user=user).order_by('-created_at')

    return render(request, 'user_dashboard.html', {'logged_user': user, 'reports': reports})


def user_logout(request):
    if 'normal_user_id' in request.session:
        del request.session['normal_user_id']
    return redirect('user_login')


def auth_logout(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


def auth_dashboard(request):
    if 'authority_user_id' not in request.session:
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


def save_location(request):
    authority_id = request.session.get('authority_user_id')
    if not authority_id:
        return JsonResponse({'error': 'Not logged in'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    data = json.loads(request.body)
    LegalDumpingLocation.objects.create(
        name=data.get('name'),
        location_type=data.get('type'),
        latitude=data.get('lat'),
        longitude=data.get('lng'),
        added_by_id=authority_id,
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


def delete_location(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'invalid'}, status=400)

    authority_id = request.session.get('authority_user_id')
    if not authority_id:
        return JsonResponse({'status': 'unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        location_id = data.get('id')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'invalid_json'}, status=400)

    location = get_object_or_404(
        LegalDumpingLocation,
        id=location_id,
        added_by_id=authority_id,
        is_active=True,
    )
    location.is_active = False
    location.save()

    return JsonResponse({'status': 'success'})
