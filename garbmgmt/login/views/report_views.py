import io
import json
import zipfile
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from ..models import GarbageReport, GarbageEvidence, Normal_user


@require_POST
def submit_garbage_report(request):
    user_id = request.session.get('normal_user_id')
    if not user_id:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    user = Normal_user.objects.get(id=user_id)
    location = request.POST.get('location')
    description = request.POST.get('description')
    severity = request.POST.get('severity')
    files = request.FILES.getlist('evidence')

    if not location or not description or not severity:
        return JsonResponse({'error': 'All fields are required'}, status=400)

    report = GarbageReport.objects.create(
        user=user,
        location=location,
        description=description,
        severity=severity,
    )

    for f in files:
        GarbageEvidence.objects.create(report=report, file=f)

    return JsonResponse({'message': 'Garbage report submitted successfully', 'report_id': report.id})


def user_reports(request):
    reports = GarbageReport.objects.prefetch_related('evidences').order_by('-created_at')
    data = [
        {
            'id': r.id,
            'reported_at': r.created_at.strftime('%Y-%m-%d %H:%M'),
            'location': r.location,
            'severity': r.severity,
            'media': [e.file.url for e in r.evidences.all()],
        }
        for r in reports
    ]
    return JsonResponse(data, safe=False)


def download_report_zip(request, report_id):
    report = get_object_or_404(GarbageReport, id=report_id)
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for ev in report.evidences.all():
            zip_file.write(ev.file.path, arcname=ev.file.name.split('/')[-1])

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename=report_{report.id}.zip'
    return response


def get_report_media(request, report_id):
    evidences = GarbageEvidence.objects.filter(report_id=report_id)
    files = [
        {
            'url': e.file.url,
            'type': 'video' if e.file.url.lower().endswith(('.mp4', '.webm', '.ogg')) else 'image',
        }
        for e in evidences
    ]
    return JsonResponse({'files': files})


@require_POST
def update_report_status(request):
    if 'authority_user_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        report_id = data.get('report_id')
        status = data.get('status')

        report = get_object_or_404(GarbageReport, id=report_id)
        report.status = status
        report.save()

        return JsonResponse({'message': 'Status updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
