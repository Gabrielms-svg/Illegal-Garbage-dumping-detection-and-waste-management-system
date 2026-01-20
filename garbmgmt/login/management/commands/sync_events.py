from django.core.management.base import BaseCommand
from login.evidence_manager import sync_and_list_events

class Command(BaseCommand):
    help = 'Syncs file system evidence events to the database'

    def handle(self, *args, **options):
        self.stdout.write("Starting synchronization...")
        sync_and_list_events()
        self.stdout.write(self.style.SUCCESS("Successfully synced events."))
