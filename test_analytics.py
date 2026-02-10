from login.models import GarbageReport
from django.db.models import Count
from django.db.models.functions import TruncDate

qs = GarbageReport.objects.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')

print('User Reports Query Results:')
for x in qs:
    print(f'  Date: {x["date"]}, Count: {x["count"]}')
print(f'\nTotal groups: {qs.count()}')
print(f'Total reports: {GarbageReport.objects.count()}')
