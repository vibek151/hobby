

from django.db import models
from core.middleware import get_current_franchise, get_current_user


# ===============================
# 🔹 TENANT MANAGER
# ===============================
class TenantManager(models.Manager):
    def get_queryset(self):
        user = get_current_user()

        # ✅ Superuser can see everything
        if user and user.is_superuser:
            return super().get_queryset()

        franchise = get_current_franchise()

        # ✅ Normal users see only their franchise data
        if franchise:
            return super().get_queryset().filter(franchise=franchise)

        # ❌ If no franchise → return nothing (safe fallback)
        return super().get_queryset().none()


# ===============================
# 🔹 BASE MULTI-TENANT MODEL
# ===============================
class MultiTenantModel(models.Model):

    franchise = models.ForeignKey(
        "franchise.Franchise",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        editable=True,  # 🔥 Prevent manual editing in admin
    )

    # ✅ Default filtered manager
    objects = TenantManager()

    # ✅ Unfiltered manager (for internal logic / signals / admin override)
    original_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):

        # If franchise already set (superuser), don't override
        if not self.franchise_id:
            franchise = get_current_franchise()

            if franchise:
                self.franchise = franchise

        super().save(*args, **kwargs)