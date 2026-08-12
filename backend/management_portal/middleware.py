import threading
import time

from django.db import close_old_connections


class NoticeSchedulerMiddleware:
    interval_seconds = 10
    _last_check = 0
    _is_running = False
    _lock = threading.Lock()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._maybe_run_scheduler()
        return self.get_response(request)

    @classmethod
    def _maybe_run_scheduler(cls):
        now = time.monotonic()

        with cls._lock:
            if cls._is_running or now - cls._last_check < cls.interval_seconds:
                return

            cls._last_check = now
            cls._is_running = True

        thread = threading.Thread(
            target=cls._run_scheduler,
            name="notice-scheduler-request",
            daemon=True
        )
        thread.start()

    @classmethod
    def _run_scheduler(cls):
        try:
            close_old_connections()

            from .scheduler import run_scheduled_notices

            run_scheduled_notices()
        except Exception as error:
            print("Notice scheduler error:", error)
        finally:
            close_old_connections()

            with cls._lock:
                cls._is_running = False
