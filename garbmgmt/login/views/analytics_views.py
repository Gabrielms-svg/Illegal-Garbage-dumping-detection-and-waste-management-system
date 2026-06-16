from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from ..models import DumpingEvent, GarbageReport, GarbageEvidence


@login_required(login_url='auth_login')
def analytics_dashboard(request):
    if not request.user.is_staff:
        return redirect('auth_login')

    cctv_time_qs = (
        DumpingEvent.objects
        .extra(select={'date': 'DATE(timestamp)'})
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    cctv_time_labels = [str(x['date']) for x in cctv_time_qs]
    cctv_time_counts = [x['count'] for x in cctv_time_qs]

    cctv_location_qs = (
        DumpingEvent.objects
        .values('illegal_location')
        .annotate(count=Count('id'))
    )
    cctv_location_labels = [x['illegal_location'] for x in cctv_location_qs]
    cctv_location_counts = [x['count'] for x in cctv_location_qs]

    user_time_qs = (
        GarbageReport.objects
        .extra(select={'date': 'DATE(created_at)'})
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    user_time_labels = [str(x['date']) for x in user_time_qs]
    user_time_counts = [x['count'] for x in user_time_qs]

    severity_qs = (
        GarbageReport.objects
        .values('severity')
        .annotate(count=Count('id'))
    )
    severity_labels = [x['severity'] for x in severity_qs]
    severity_counts = [x['count'] for x in severity_qs]

    user_location_qs = (
        GarbageReport.objects
        .values('location')
        .annotate(count=Count('id'))
    )
    user_location_labels = [x['location'] for x in user_location_qs]
    user_location_counts = [x['count'] for x in user_location_qs]

    evidence_qs = (
        GarbageEvidence.objects
        .values('report_id')
        .annotate(count=Count('id'))
    )
    evidence_report_labels = [f"Report {x['report_id']}" for x in evidence_qs]
    evidence_report_counts = [x['count'] for x in evidence_qs]

    hotspot_labels = list(set(cctv_location_labels) | set(user_location_labels))
    hotspot_cctv_counts = [
        next((x['count'] for x in cctv_location_qs if x['illegal_location'] == loc), 0)
        for loc in hotspot_labels
    ]
    hotspot_user_counts = [
        next((x['count'] for x in user_location_qs if x['location'] == loc), 0)
        for loc in hotspot_labels
    ]

    combined_time_labels = sorted(set(cctv_time_labels) | set(user_time_labels))
    combined_cctv_counts = [
        cctv_time_counts[cctv_time_labels.index(d)] if d in cctv_time_labels else 0
        for d in combined_time_labels
    ]
    combined_user_counts = [
        user_time_counts[user_time_labels.index(d)] if d in user_time_labels else 0
        for d in combined_time_labels
    ]

    severity_vs_cctv_labels = severity_labels
    severity_vs_cctv_counts = [
        DumpingEvent.objects.filter(illegal_location__icontains=sev).count()
        for sev in severity_labels
    ]

    camera_qs = (
        DumpingEvent.objects
        .values('camera__camera_id')
        .annotate(count=Count('id'))
    )
    camera_labels = [x['camera__camera_id'] for x in camera_qs]
    camera_efficiency_counts = [x['count'] for x in camera_qs]

    context = {
        'cctv_time_labels': cctv_time_labels,
        'cctv_time_counts': cctv_time_counts,
        'cctv_location_labels': cctv_location_labels,
        'cctv_location_counts': cctv_location_counts,
        'user_time_labels': user_time_labels,
        'user_time_counts': user_time_counts,
        'severity_labels': severity_labels,
        'severity_counts': severity_counts,
        'user_location_labels': user_location_labels,
        'user_location_counts': user_location_counts,
        'evidence_report_labels': evidence_report_labels,
        'evidence_report_counts': evidence_report_counts,
        'hotspot_labels': hotspot_labels,
        'hotspot_cctv_counts': hotspot_cctv_counts,
        'hotspot_user_counts': hotspot_user_counts,
        'combined_time_labels': combined_time_labels,
        'combined_cctv_counts': combined_cctv_counts,
        'combined_user_counts': combined_user_counts,
        'severity_vs_cctv_labels': severity_vs_cctv_labels,
        'severity_vs_cctv_counts': severity_vs_cctv_counts,
        'camera_labels': camera_labels,
        'camera_efficiency_counts': camera_efficiency_counts,
    }
    return render(request, 'analytics.html', context)
