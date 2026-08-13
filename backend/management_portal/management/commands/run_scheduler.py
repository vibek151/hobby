import time

from django.core.management.base import BaseCommand
from management_portal.scheduler import run_scheduled_notices


class Command(BaseCommand):
    help = "Run the scheduled notice/email system continuously."

    def handle(self, *args, **options):
        self.stdout.write("Notice scheduler started.")

        while True:
            try:
                run_scheduled_notices()
            except Exception as e:
                self.stderr.write(f"Scheduler error: {e}")

            time.sleep(20)