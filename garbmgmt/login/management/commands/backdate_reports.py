from django.core.management.base import BaseCommand
from login.models import GarbageReport
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Backdate existing garbage reports across different days for analytics testing'

    def handle(self, *args, **options):
        reports = GarbageReport.objects.all().order_by('created_at')
        
        if reports.count() == 0:
            self.stdout.write(self.style.ERROR('[X] No reports found. Please submit some reports first.'))
            return
        
        self.stdout.write(f'[*] Found {reports.count()} report(s). Backdating across last 7 days...')
        
        base_date = timezone.now()
        
        for i, report in enumerate(reports):
            # Distribute reports across last 7 days
            days_ago = i % 7
            new_date = base_date - timedelta(days=days_ago)
            
            report.created_at = new_date
            report.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'[OK] Report #{report.id} backdated to {new_date.strftime("%Y-%m-%d %H:%M")}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n[DONE] {reports.count()} reports spread across the last 7 days.'
            )
        )
        self.stdout.write('[*] Refresh the Analytics page to see the charts with data!')
