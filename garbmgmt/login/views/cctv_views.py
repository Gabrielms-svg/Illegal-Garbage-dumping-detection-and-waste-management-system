import csv
import cv2
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from ..models import DumpingEvent
from datetime import datetime

RTSP_URL = 'rtsp://localhost:8554/cam1'


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
        content_type='multipart/x-mixed-replace; boundary=frame',
    )


def cctv_detected_events(request):
    events_qs = DumpingEvent.objects.select_related('camera').prefetch_related('plates').order_by('-timestamp')
    events = []
    for e in events_qs:
        plate = e.plates.first()
        events.append({
            'event_id': e.event_id,
            'camera_id': e.camera.camera_id if e.camera else None,
            'location': e.illegal_location,
            'timestamp': e.timestamp.isoformat() if e.timestamp else None,
            'plate_image': plate.image.url if plate and plate.image else None,
            'confidence': None,
            'video': e.dumping_video.name if e.dumping_video else None,
        })
    return JsonResponse(events, safe=False)


def cctv_events(request):
    events_qs = DumpingEvent.objects.select_related('camera').prefetch_related('plates').order_by('-timestamp')
    events = []
    for e in events_qs:
        plate = e.plates.first()
        events.append({
            'event_id': e.event_id,
            'camera_id': e.camera.camera_id if e.camera else None,
            'location': e.illegal_location,
            'timestamp': e.timestamp.isoformat() if e.timestamp else None,
            'plate_image': plate.image.url if plate and plate.image else None,
            'dumping_video': e.dumping_video.name if e.dumping_video else None,
        })
    return JsonResponse(events, safe=False)


def cctv_event_detail(request, id):
    event = get_object_or_404(DumpingEvent, id=id)
    return JsonResponse({
        'event_id': event.event_id,
        'location': event.illegal_location,
        'video_url': event.dumping_video.url if event.dumping_video else None,
    })


def api_cctv_events(request):
    if 'authority_user_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    qs = DumpingEvent.objects.select_related('camera').prefetch_related('plates')
    date_str = request.GET.get('date')
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            qs = qs.filter(timestamp__date=date_obj)
        except ValueError:
            pass

    sort_by = request.GET.get('sort', 'recent')
    if sort_by == 'oldest':
        qs = qs.order_by('timestamp')
    elif sort_by == 'location':
        qs = qs.order_by('illegal_location', '-timestamp')
    else:
        qs = qs.order_by('-timestamp')

    export_fmt = request.GET.get('export')
    if export_fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="cctv_report_{now().strftime("%Y%m%d_%H%M")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Event ID', 'Camera', 'Location', 'Timestamp', 'Plates', 'Confidence'])
        for event in qs:
            plates = ', '.join([p.plate_text for p in event.plates.all()])
            writer.writerow([
                event.event_id,
                event.camera.camera_id if event.camera else 'Unknown',
                event.illegal_location,
                event.timestamp.strftime('%Y-%m-%d %H:%M:%S') if event.timestamp else '',
                plates,
                'N/A',
            ])
        return response

    data = []
    for event in qs:
        plate_obj = event.plates.first()
        plate_url = plate_obj.image.url if (plate_obj and plate_obj.image) else None
        data.append({
            'id': event.id,
            'event_id': event.event_id,
            'timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M:%S') if event.timestamp else '',
            'location': event.illegal_location,
            'video_url': event.dumping_video.url if event.dumping_video else '',
            'plate_image': plate_url,
        })

    return JsonResponse({'events': data})
