from django.urls import path
from . import views

urlpatterns = [
    # ---------- EMAIL OTP ----------
    path("send-email-otp/", views.send_email_otp, name="send_email_otp"),
    path("verify-email-otp/", views.verify_email_otp, name="verify_email_otp"),

    # ---------- LOGIN ----------
    path("login/", views.franchise_login, name="franchise_login"),

    # ---------- PASSWORD RESET ----------
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("force-reset/", views.force_reset, name="force_reset"),

    # ---------- EMAIL CHANGE ----------
    path("send-email-change-otp/", views.send_email_change_otp, name="send_email_change_otp"),
    path("send-old-email-otp/", views.send_old_email_otp, name="send_old_email_otp"),
    path("send-new-email-otp/", views.send_new_email_otp, name="send_new_email_otp"),
    path("update-email/", views.update_email, name="update_email"),

    # ---------- ACCOUNT CHANGE (Added Names) ----------
    path("send-account-change-otp/", views.send_account_change_otp, name="send_account_change_otp"),
    path("verify-account-change/", views.verify_account_change, name="verify_account_change"),
    
    # ---------- RESTRICTION & LOGOUT ----------
    # path("login/", views.franchise_login, name="franchise_login"),
    path("logout-restricted/", views.logout_restricted, name="logout_restricted"),
    path("restricted/", views.restricted_page, name="restricted_page"),
    path("check-restriction/", views.check_restriction, name="check_restriction"),
]