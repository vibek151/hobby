from django.apps import AppConfig
from django.urls import reverse
from django.utils.html import format_html

class EditButtonMixin:
    def edit_button(self, obj):
        model_name = obj._meta.model_name
        app_label = obj._meta.app_label
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.id])
        return format_html('<a class="button" href="{}">✏ Edit</a>', url)

    edit_button.short_description = "Edit"


from django.apps import AppConfig

class PortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portal"
    verbose_name = "Student Portal"   # 👈 THIS FIXES ADMIN CATEGORY NAME
