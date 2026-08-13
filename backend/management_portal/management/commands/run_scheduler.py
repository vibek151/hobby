from django.core.management.base import BaseCommand
from management_portal.scheduler import run_scheduled_notices


class Command(BaseCommand):
    help = "Run scheduled notices once."

    def handle(self, *args, **options):
        self.stdout.write("Running scheduled notices...")
        run_scheduled_notices()
        self.stdout.write("Scheduler check completed.")