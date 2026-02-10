"""
Script to backdate some garbage reports for analytics testing.
This will modify the created_at dates of existing reports to spread them across multiple days.

Run this script from your Django project directory:
python manage.py shell < backdate_reports.py
"""

from login.models import GarbageReport
from datetime import datetime, timedelta
from django.utils import timezone

# Get all reports
reports = GarbageReport.objects.all().order_by('created_at')

if reports.count() == 0:
    print("❌ No reports found. Please submit some reports first through the User Dashboard.")
else:
    print(f"📊 Found {reports.count()} report(s). Backdating them across different days...")
    
    # Spread reports across the last 7 days
    base_date = timezone.now()
    
    for i, report in enumerate(reports):
        # Distribute reports across last 7 days
        days_ago = i % 7
        new_date = base_date - timedelta(days=days_ago)
        
        report.created_at = new_date
        report.save()
        
        print(f"✅ Report #{report.id} backdated to {new_date.strftime('%Y-%m-%d %H:%M')}")
    
    print(f"\n🎉 Done! {reports.count()} reports have been spread across the last 7 days.")
    print("📈 Refresh the Analytics page to see the 'User Reports Over Time' chart with data!")
