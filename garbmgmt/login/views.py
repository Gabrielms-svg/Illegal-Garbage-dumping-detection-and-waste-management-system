from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth import authenticate , login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import re,os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import JsonResponse
from .chatbot import get_response
import json
from .models import LegalDumpingLocation
from django.views.decorators.http import require_http_methods
import cv2
from django.http import StreamingHttpResponse
from .evidence_manager import sync_and_list_events
from .models import DumpingEvent
from .models import GarbageReport, GarbageEvidence,Normal_user
import zipfile
import io
from django.conf import settings
from django.db.models import Count
from django.db.models.functions import TruncDate


def home(request):
    events = sync_and_list_events()
    return render(request, 'home.html', {"events": events})


def user_register(request):
     if request.method == "POST":
        profile = request.FILES.get('profile')
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            return redirect('user_register')

        result = Normal_user.objects.create(profile=profile, phone=phone, fullname=fullname, 	email=email, password=make_password(password2))
        result.save()

     return render(request,'user_register.html' )




def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = Normal_user.objects.get(email=email)

            # check hashed password
            if check_password(password, user.password):
                request.session["normal_user_id"] = user.id
                request.session["normal_user_name"] = user.fullname
                return redirect("user_dashboard")
            else:
                messages.error(request, "Invalid password")
                return redirect("user_login")

        except Normal_user.DoesNotExist:
            messages.error(request, "User not found")
            return redirect("user_login")

    return render(request, "user_login.html")


def auth_login(request):
    if request.method == "POST":
        auth_id = request.POST.get("auth_id")
        password = request.POST.get("password")

        try:
            user = Authority_user.objects.get(auth_id=auth_id)

            if user.password == password:  # direct comparison
                request.session['authority_user_id'] = user.id
                messages.success(request, "Authority Login Successful!")
                return redirect("auth_dashboard")
            else:
                messages.error(request, "Invalid password!")
                return redirect("auth_login")

        except Authority_user.DoesNotExist:
            messages.error(request, "Invalid Authority ID!")
            return redirect("auth_login")

    return render(request, "auth_login.html")


def user_dashboard(request):
    if 'normal_user_id' not in request.session:
        return redirect('user_login')
    user = Normal_user.objects.get(id=request.session['normal_user_id'])

    context = {
        'logged_user': user,

    }
    return render(request, 'user_dashboard.html')


@csrf_exempt
def chatbot_api(request):
    print("VIEW HIT ✔")                     # Debug
    print("POST:", request.POST)            # Debug

    if request.method == "POST":
        user_message = request.POST.get("message", "")
        print("USER MESSAGE:", user_message)  # Debug

        reply = get_response(user_message)
        return JsonResponse({"reply": reply})

    return JsonResponse({"error": "Invalid request"}, status=400)

def user_logout(request):
    if 'normal_user_id' in request.session:
        del request.session['normal_user_id']
    return redirect('user_login')
  # redirect to login page

def auth_logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('home')


def auth_dashboard(request):
    if 'authority_user_id' not in request.session:
        return redirect('auth_login')
    
    reports = GarbageReport.objects.prefetch_related("evidences").order_by("-created_at")

    
    cctv_events = DumpingEvent.objects.all().order_by('-timestamp')
    context = {
        "cctv_events": cctv_events,
        "reports": reports
    }
    return render(request,'auth_dashboard.html',context)



@csrf_exempt  # (later you can do CSRF properly)
def save_location(request):

    authority_id = request.session.get("authority_user_id")
    if not authority_id:
        return JsonResponse({"error": "Not logged in"}, status=401)

    authority = Authority_user.objects.get(id=authority_id)

    if request.method == "POST":
        data = json.loads(request.body)

        location = LegalDumpingLocation.objects.create(
            name=data.get("name"),
            location_type=data.get("type"),
            latitude=data.get("lat"),
            longitude=data.get("lng"),
            added_by=authority
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"error": "Invalid request"}, status=400)




def get_locations(request):
    locations = LegalDumpingLocation.objects.filter(is_active=True)

    data = []
    for loc in locations:
        data.append({
            "id": loc.id,
            "name": loc.name,
            "type": loc.location_type,
            "lat": loc.latitude,
            "lng": loc.longitude
        })

    return JsonResponse(data, safe=False)






def delete_location(request):
    if request.method != "POST":
        return JsonResponse({"status": "invalid"}, status=400)

    authority_id = request.session.get("authority_user_id")
    if not authority_id:
        return JsonResponse({"status": "unauthorized"}, status=403)

    try:
        data = json.loads(request.body)
        location_id = data.get("id")
    except json.JSONDecodeError:
        return JsonResponse({"status": "invalid_json"}, status=400)

    location = get_object_or_404(
        LegalDumpingLocation,
        id=location_id,
        added_by_id=authority_id,
        is_active=True
    )

    # ✅ SOFT DELETE
    location.is_active = False
    location.save()

    return JsonResponse({"status": "success"})





RTSP_URL = "rtsp://localhost:8554/cam1"

def gen_frames():
    cap = cv2.VideoCapture(RTSP_URL)

    while True:
        success, frame = cap.read()
        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def live_camera_feed(request):
    return StreamingHttpResponse(
        gen_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )






@require_POST
def submit_garbage_report(request):

    user_id = request.session.get("normal_user_id")
    if not user_id:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    user = Normal_user.objects.get(id=user_id)

    location = request.POST.get("location")
    description = request.POST.get("description")
    severity = request.POST.get("severity")
    files = request.FILES.getlist("evidence")

    if not location or not description or not severity:
        return JsonResponse({"error": "All fields are required"}, status=400)

    report = GarbageReport.objects.create(
        user=user,
        location=location,
        description=description,
        severity=severity
    )

    for f in files:
        GarbageEvidence.objects.create(
            report=report,
            file=f
        )

    return JsonResponse({
        "message": "Garbage report submitted successfully",
        "report_id": report.id
    })

       

def user_reports(request):
    reports = GarbageReport.objects.prefetch_related("evidences").order_by("-created_at")

    data = []
    for r in reports:
        data.append({
            "id": r.id,
            "reported_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "location": r.location,
            "severity":r.severity,
            "media": [e.file.url for e in r.evidences.all()]
        })

    # return JsonResponse(data, safe=False)
    # return render(request,)



def download_report_zip(request, report_id):
    report = GarbageReport.objects.get(id=report_id)

    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')

    for ev in report.evidences.all():
        zip_file.write(ev.file.path, arcname=ev.file.name.split("/")[-1])

    zip_file.close()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename=report_{report.id}.zip'

    return response

def get_report_media(request, report_id):
    evidences = GarbageEvidence.objects.filter(report_id=report_id)

    files = []
    for e in evidences:
        url = e.file.url
        files.append({
            "url": url,
            "type": "video" if url.lower().endswith((".mp4", ".webm", ".ogg")) else "image"
        })

    return JsonResponse({"files": files})



def cctv_detected_events(request):
    events = []

    base_path = settings.EVIDENCE_ROOT  # login/evidence

    for cam in os.listdir(base_path):
        cam_path = os.path.join(base_path, cam)

        if not os.path.isdir(cam_path):
            continue

        for event_folder in os.listdir(cam_path):
            event_path = os.path.join(cam_path, event_folder)
            json_path = os.path.join(event_path, "event.json")

            if not os.path.exists(json_path):
                continue

            with open(json_path, "r") as f:
                data = json.load(f)

            # Extract first plate (if any)
            plate_img = None
            plate_conf = None

            if data.get("plates"):
                plate_img = data["plates"][0].get("image")
                plate_conf = data["plates"][0].get("confidence")

            events.append({
                "event_id": data.get("event_id"),
                "camera_id": data.get("camera_id"),
                "location": data.get("location"),
                "timestamp": data.get("timestamp"),
                "plate_image": plate_img,
                "confidence": plate_conf,
                "video": data.get("dumping_video"),
            })

    return JsonResponse(events, safe=False)

# views.py


def cctv_events(request):
    base_dir = os.path.join(settings.BASE_DIR, "login", "evidence")
    events = []

    for cam in os.listdir(base_dir):
        cam_path = os.path.join(base_dir, cam)

        if not os.path.isdir(cam_path):
            continue

        for event_folder in os.listdir(cam_path):
            event_path = os.path.join(cam_path, event_folder, "event.json")

            if os.path.exists(event_path):
                with open(event_path, "r") as f:
                    data = json.load(f)

                    # add relative media paths
                    data["camera_id"] = cam
                    data["plate_image"] = f"login/evidence/{cam}/{event_folder}/{data.get('plate_image','')}"
                    data["timestamp"] = data.get("timestamp")

                    events.append(data)

    return JsonResponse(events, safe=False)

def cctv_event_detail(request, id):
    event = get_object_or_404(DumpingEvent, id=id)
    return JsonResponse({
        "event_id": event.event_id,
        "location": event.illegal_location,
        "video_url": event.dumping_video.url
    })


def analytics_dashboard(request):
    if 'authority_user_id' not in request.session:
        return redirect('auth_login')

    # ================= CCTV ANALYTICS =================

    # 1. Dumping events over time
    cctv_time_qs = (
        DumpingEvent.objects
        .annotate(date=TruncDate('timestamp'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    cctv_time_labels = [str(x['date']) for x in cctv_time_qs]
    cctv_time_counts = [x['count'] for x in cctv_time_qs]

    # 2. Dumping frequency by location
    cctv_location_qs = (
        DumpingEvent.objects
        .values('illegal_location')
        .annotate(count=Count('id'))
    )

    cctv_location_labels = [x['illegal_location'] for x in cctv_location_qs]
    cctv_location_counts = [x['count'] for x in cctv_location_qs]


    # ================= USER ANALYTICS =================

    # 3. User reports over time
    user_time_qs = (
        GarbageReport.objects
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    user_time_labels = [str(x['date']) for x in user_time_qs]
    user_time_counts = [x['count'] for x in user_time_qs]

    # 4. Reports by severity
    severity_qs = (
        GarbageReport.objects
        .values('severity')
        .annotate(count=Count('id'))
    )

    severity_labels = [x['severity'] for x in severity_qs]
    severity_counts = [x['count'] for x in severity_qs]

    # 5. Reports by location
    user_location_qs = (
        GarbageReport.objects
        .values('location')
        .annotate(count=Count('id'))
    )

    user_location_labels = [x['location'] for x in user_location_qs]
    user_location_counts = [x['count'] for x in user_location_qs]

    # 6. Evidence count per report
    evidence_qs = (
        GarbageEvidence.objects
        .values('report_id')
        .annotate(count=Count('id'))
    )

    evidence_report_labels = [f"Report {x['report_id']}" for x in evidence_qs]
    evidence_report_counts = [x['count'] for x in evidence_qs]


    # ================= COMBINED ANALYTICS =================

    # 7. Hotspot comparison (same location name assumed)
    hotspot_labels = list(
        set(cctv_location_labels) | set(user_location_labels)
    )

    hotspot_cctv_counts = [
        next((x['count'] for x in cctv_location_qs if x['illegal_location'] == loc), 0)
        for loc in hotspot_labels
    ]

    hotspot_user_counts = [
        next((x['count'] for x in user_location_qs if x['location'] == loc), 0)
        for loc in hotspot_labels
    ]

    # 8. Dumping vs User participation (time)
    combined_time_labels = sorted(
        set(cctv_time_labels) | set(user_time_labels)
    )

    combined_cctv_counts = [
        cctv_time_counts[cctv_time_labels.index(d)] if d in cctv_time_labels else 0
        for d in combined_time_labels
    ]

    combined_user_counts = [
        user_time_counts[user_time_labels.index(d)] if d in user_time_labels else 0
        for d in combined_time_labels
    ]

    # 9. Severity vs CCTV detection
    severity_vs_cctv_labels = severity_labels
    severity_vs_cctv_counts = [
        DumpingEvent.objects.filter(illegal_location__icontains=sev).count()
        for sev in severity_labels
    ]

    # 10. Camera efficiency
    camera_qs = (
        DumpingEvent.objects
        .values('camera__camera_id')
        .annotate(count=Count('id'))
    )

    camera_labels = [x['camera__camera_id'] for x in camera_qs]
    camera_efficiency_counts = [x['count'] for x in camera_qs]


    context = {
        "cctv_time_labels": cctv_time_labels,
        "cctv_time_counts": cctv_time_counts,

        "cctv_location_labels": cctv_location_labels,
        "cctv_location_counts": cctv_location_counts,

        "user_time_labels": user_time_labels,
        "user_time_counts": user_time_counts,

        "severity_labels": severity_labels,
        "severity_counts": severity_counts,

        "user_location_labels": user_location_labels,
        "user_location_counts": user_location_counts,

        "evidence_report_labels": evidence_report_labels,
        "evidence_report_counts": evidence_report_counts,

        "hotspot_labels": hotspot_labels,
        "hotspot_cctv_counts": hotspot_cctv_counts,
        "hotspot_user_counts": hotspot_user_counts,

        "combined_time_labels": combined_time_labels,
        "combined_cctv_counts": combined_cctv_counts,
        "combined_user_counts": combined_user_counts,

        "severity_vs_cctv_labels": severity_vs_cctv_labels,
        "severity_vs_cctv_counts": severity_vs_cctv_counts,

        "camera_labels": camera_labels,
        "camera_efficiency_counts": camera_efficiency_counts,
    }

    return render(request, "analytics.html", context)
