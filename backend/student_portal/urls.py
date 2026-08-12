

from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import send_otp
from .views import verify_otp
from .views import get_profile, get_recent_notices
urlpatterns = [
    # Dashboard & Pages
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("payments/", views.student_payments, name="student_payments"),
    path("pay/", views.make_payment, name="make_payment"),
    path("franchiseaccount/", views.franchise_account, name="franchise_account"),

    # EMAIL & ACCOUNT UPDATE
    path("verify-account-change/", views.verify_account_change, name="verify_account_change"),
    path("update-password/", views.update_password, name="update_password"),
    path("update-email/", views.update_email, name="update_email"),
    path("send-old-email-otp/", views.send_old_email_otp, name="send_old_email_otp"),
    path("send-new-email-otp/", views.send_new_email_otp, name="send_new_email_otp"),

    # APIs
    path("get-course-data/", views.get_course_data, name="get_course_data"),
    path("get-student-data/", views.get_student_data, name="get_student_data"),

    # PDF & Statements
    # path("admission-pdf/<int:pk>/", views.generate_admission_form, name="admission_pdf"),
    path("statement/<path:student_id>/", views.student_statement, name="student_statement"),

    path(
        "calculate-fee/",
        views.calculate_fee,
        name="calculate_fee",
    ),
    path(
        "send-otp/",
        send_otp,
        name="send_otp"
    ),
    path(
        "verify-otp/",
        verify_otp,
        name="verify_otp"
    ),
    path(
        "profile/",
        views.get_profile,
        name="profile"
    ),
    path(
        "course-history/",
        views.get_course_history
    ),
    path(
        "marks/",
        views.get_marks
    ),
    path(
        "payments-api/",
        views.get_payments
    ),
    path(
        "certificates-api/",
        views.get_certificates
    ),
    path(
        "notices-api/",
        views.get_notices
    ),
    path(
        "recent-notices/",
        get_recent_notices
    ),
    path(
        "download-my-pdf/",
        views.student_pdf,
        name="student_pdf"
    ),
    path(
    "download-statement/",
        views.download_statement,
        name="download_statement"
    ),
    path(
        "download-certificate/",
        views.download_certificate,
        name="download_certificate"
    ),

    path(
        "download-marksheet/",
        views.download_marksheet,
        name="download_marksheet"
    ),
    # path("api/home-courses/", get_courses),
    path(
        "verify-certificate/",
        views.verify_certificate
    ),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



