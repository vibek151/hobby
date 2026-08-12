import os
import sys
import threading
import time

from django.conf import settings
from django.db import close_old_connections


_scheduler_started = False
_scheduler_lock = threading.Lock()


def start_notice_scheduler(interval_seconds=20):
    global _scheduler_started

    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command != "runserver":
        return

    run_main = os.environ.get("RUN_MAIN")
    using_reloader = "--noreload" not in sys.argv
    if settings.DEBUG and using_reloader and run_main != "true":
        return

    with _scheduler_lock:
        if _scheduler_started:
            return

        _scheduler_started = True

    thread = threading.Thread(
        target=_notice_scheduler_loop,
        args=(interval_seconds,),
        name="notice-scheduler",
        daemon=True
    )
    thread.start()
    print(f"Notice scheduler started. Checking every {interval_seconds} seconds.")


def _notice_scheduler_loop(interval_seconds):
    time.sleep(5)

    while True:
        try:
            close_old_connections()

            from .scheduler import run_scheduled_notices

            run_scheduled_notices()
        except Exception as error:
            print("Notice scheduler error:", error)
        finally:
            close_old_connections()
            time.sleep(interval_seconds)
