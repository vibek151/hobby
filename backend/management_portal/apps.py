from django.apps import AppConfig


class ManagementPortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "management_portal"
    verbose_name = "MANAGEMENT PORTAL"

    def ready(self):
        from .scheduler_service import start_notice_scheduler

        start_notice_scheduler()
