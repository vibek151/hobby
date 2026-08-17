

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from institute.forms import MailjetPasswordResetForm
from student_portal.views import batchlistview, custom_logout
# from institute.views import forgot_username, CustomAdminLoginView  # ✅ important
from institute.views import forgot_username
from institute.views import health_check



urlpatterns = [

    # 🔐 PASSWORD RESET (keep as is)
    # path("admin/password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(
            form_class=MailjetPasswordResetForm
        ),
        name="password_reset",
    ),
    path("admin/password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # 🔐 EXTRA FEATURES (keep as is)
    path('forgot-username/', forgot_username, name="forgot_username"),
    path('admin/logout/', custom_logout, name='logout'),

    # 🔥 ONLY LOGIN OVERRIDE (IMPORTANT)
    # path("admin/login/", CustomAdminLoginView.as_view(), name="admin_login"),

    # 🧠 DEFAULT ADMIN (unchanged)
    path("admin/", admin.site.urls),

    # 🌐 APP ROUTES (unchanged)
    path("", include("portal.urls")),
    # path("student/", include("student_portal.urls")),
    path("franchise/", include("franchise.urls")),
    # path("", include("student_portal.urls")),

    # 📊 CUSTOM ADMIN VIEW (unchanged)
    path(
        "admin/student_portal/batchlistview/",
        batchlistview,
        name="batchlistview"
    ),
    path("student/", include("student_portal.urls")),
    path("api/website/", include("website_portal.urls")),
    path("api/management/", include("management_portal.urls")),
    path("health/", health_check, name="health_check"),

]


# 📁 MEDIA (keep as is)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )