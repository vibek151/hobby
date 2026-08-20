from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from student_portal.notifications import send_student_email
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import random
import secrets
import requests
import os
from .models import Franchise
from .utils import generate_temp_code, generate_otp
from django.core.cache import cache




def send_email_otp(request):

    if request.method == "POST":

        email = request.POST.get("email")

        otp = ''.join(str(secrets.randbelow(10)) for _ in range(6))

        response = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(
                os.environ["MAILJET_API_KEY"],
                os.environ["MAILJET_SECRET_KEY"],
            ),
            json={
                "Messages": [
                    {
                        "From": {
                            "Email": "smartcomputerins2022@gmail.com",
                            "Name": "Smart Computer Institute",
                        },
                        "To": [
                            {
                                "Email": email,
                            }
                        ],
                        "Subject": "Email Verification OTP | Smart Computer Institute",
                        "TextPart": (
                            f"Dear User,\n\n"
                            f"Your email verification OTP is: {otp}\n\n"
                            f"This OTP is valid for 5 minutes.\n\n"
                            f"Regards,\n"
                            f"Smart Computer Institute"
                        ),
                    }
                ]
            },
            timeout=30,
        )

        response.raise_for_status()

        request.session["email_otp"] = str(otp)
        request.session["email_otp_time"] = timezone.now().timestamp()

        return JsonResponse({"status": "sent"})

    return JsonResponse({"status": "error"}, status=400)



def verify_email_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")

        session_otp = request.session.get("email_otp")
        otp_time = request.session.get("email_otp_time")

        if not session_otp:
            return JsonResponse({"status": "expired"})

        # ⏱ OTP expires after 5 minutes
        if otp_time and (timezone.now().timestamp() - otp_time > 300):
            return JsonResponse({"status": "expired"})

        if str(otp) == str(session_otp):
            request.session["email_verified"] = True
            request.session.modified = True

            # 🔥 cleanup
            request.session.pop("email_otp", None)
            request.session.pop("email_otp_time", None)

            return JsonResponse({"status": "verified"})
        else:
            return JsonResponse({"status": "invalid"})

    return JsonResponse({"status": "error"}, status=400)




def forgot_password(request):

    if request.method == "POST":

        username = request.POST.get("username")

        try:
            franchise = Franchise.objects.get(user__username=username)

        except Franchise.DoesNotExist:
            return render(request, "forgot.html", {"error": "User not found"})

        # CHECK IF ACCOUNT IS TEMPORARILY LOCKED
        if franchise.reset_lock_until and franchise.reset_lock_until > timezone.now():

            remaining_time = franchise.reset_lock_until - timezone.now()

            minutes = int(remaining_time.total_seconds() // 60)

            return render(
                request,
                "forgot.html",
                {"error": f"Password reset locked. Try again after {minutes} minutes."}
            )

        # GENERATE TEMP LOGIN CODE
        code = generate_temp_code()

        franchise.reset_code = code
        franchise.reset_code_expiry = timezone.now() + timedelta(minutes=10)

        # RESET SECURITY STATE
        franchise.reset_attempts = 0
        franchise.reset_otp = None
        franchise.reset_otp_expiry = None
        franchise.force_password_change = False

        franchise.save()

        # SAFER EMAIL SELECTION
        email = franchise.user.email or franchise.email

        if not email:
            return render(
                request,
                "forgot.html",
                {"error": "No email registered for this account."}
            )

        response = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(
                os.environ["MAILJET_API_KEY"],
                os.environ["MAILJET_SECRET_KEY"]
            ),
            json={
                "Messages": [{
                    "From": {
                        "Email": "smartcomputerins2022@gmail.com",
                        "Name": "Smart Computer Institute"
                    },
                    "To": [
                        {"Email": email}
                    ],
                    "Subject": "Password Recovery",
                    "TextPart": (
                        f"Your temporary login code: {code}\n\n"
                        "This code will expire in 10 minutes."
                    )
                }]
            }
        )

        response.raise_for_status()

        return render(request, "forgot.html", {"success": "Code sent to your email."})

    return render(request, "forgot.html")




def franchise_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        # NORMAL LOGIN
        user = authenticate(request, username=username, password=password)

        if user is not None:

            franchise = Franchise.objects.filter(user=user).first()

            if franchise and franchise.is_restricted:
                return render(
                    request,
                    "franchise/restricted.html",
                    {"manager_name": franchise.manager_name}
                )

            login(request, user)
            return redirect("dashboard")

        # TEMP RESET CODE LOGIN
        franchise = Franchise.objects.filter(user__username=username).first()

        if franchise and password == franchise.reset_code:

            if franchise.reset_code_expiry and franchise.reset_code_expiry > timezone.now():

                # 🔥 ADD THIS CHECK
                # 🔥 ADD THIS CHECK
                if franchise and franchise.is_restricted:
                    return render(
                        request,
                        "franchise/restricted.html",
                        {"manager_name": franchise.manager_name}
                    )

                franchise.force_password_change = True
                franchise.save()

                login(request, franchise.user)

                return redirect("force_reset")

        return render(request, "login.html", {"error": "Invalid login"})

    return render(request, "login.html")



def force_reset(request):

    franchise = Franchise.objects.get(user=request.user)

    if request.method == "POST":

        temp_code = request.POST.get("temp_code")
        otp = request.POST.get("otp")
        new_password = request.POST.get("password")

        if temp_code != franchise.reset_code:
            return render(request,"reset.html",{"error":"Invalid code"})

        if otp != franchise.reset_otp:
            return render(request,"reset.html",{"error":"Invalid OTP"})

        franchise.user.set_password(new_password)
        franchise.user.save()

        franchise.reset_code = None
        franchise.reset_otp = None
        franchise.force_password_change = False

        franchise.save()

        return redirect("franchise_login")

    otp = generate_otp()

    franchise.reset_otp = otp
    franchise.reset_otp_expiry = timezone.now() + timedelta(minutes=10)

    franchise.save()

    send_mail(
        "Password Reset OTP",
        f"Your OTP is {otp}",
        "smartcomputerins2022@gmail.com",
        [franchise.user.email],
    )

    return render(request,"reset.html")



def send_email_change_otp(request):

    email = request.POST.get("email")

    otp = str(random.randint(100000, 999999))

    request.session["email_change_otp"] = otp

    send_mail(
        "Email Change OTP",
        f"Your OTP is {otp}",
        "smartcomputerins2022@gmail.com",
        [email],
    )

    return JsonResponse({"status": "sent"})

@login_required
def send_old_email_otp(request):

    franchise = Franchise.objects.filter(user=request.user).first()

    email = None

    # ✅ PRIORITY: franchise email
    if franchise and franchise.email:
        email = franchise.email

    # ✅ fallback: user email
    elif request.user.email:
        email = request.user.email

    if not email:
        return JsonResponse({"error": "No email found"}, status=400)

    otp = str(random.randint(100000,999999))

    request.session["old_email_otp"] = otp

    # print("OLD EMAIL OTP:", otp)
    # print("SEND TO:", email)

    send_mail(
        "Verify Old Email",
        f"OTP: {otp}",
        "smartcomputerins2022@gmail.com",
        [email],
        fail_silently=False
    )

    return JsonResponse({"status":"sent"})

@login_required
def send_new_email_otp(request):

    email = request.POST.get("email")

    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)

    otp = str(random.randint(100000,999999))

    request.session["new_email_otp"] = otp

    # print("NEW EMAIL OTP:", otp)
    # print("SEND TO:", email)

    send_mail(
        "Verify New Email",
        f"OTP: {otp}",
        "smartcomputerins2022@gmail.com",
        [email],
        fail_silently=False
    )

    return JsonResponse({"status":"sent"})
@login_required
def update_email(request):

    new_email = request.POST.get("email")
    old_otp = request.POST.get("old_otp")
    new_otp = request.POST.get("new_otp")

    if old_otp != request.session.get("old_email_otp"):
        return JsonResponse({"status": "invalid_old_otp"})

    if new_otp != request.session.get("new_email_otp"):
        return JsonResponse({"status": "invalid_new_otp"})

    franchise = Franchise.objects.filter(user=request.user).first()

    if franchise:
        # ✅ Only update if exists
        franchise.email = new_email
        franchise.save()

    from django.contrib.auth import logout  # add at top if not added

    request.user.email = new_email
    request.user.save()

    # 🔥 LOGOUT HERE
    logout(request)

    request.session.pop("old_email_otp", None)
    request.session.pop("new_email_otp", None)

    return JsonResponse({
        "status": "success",
        "message": "Email updated successfully! Please login again."
    })


@login_required
def send_account_change_otp(request):

    franchise = Franchise.objects.filter(user=request.user).first()

    email = None

    # ✅ PRIORITY: franchise email
    if franchise and franchise.email:
        email = franchise.email

    # ✅ fallback: user email
    elif request.user.email:
        email = request.user.email

    if not email:
        return JsonResponse({"error": "No email found for this account"}, status=400)

    otp = str(random.randint(100000, 999999))

    # print("OTP:", otp)
    # print("SEND TO:", email)

    request.session["account_change_otp"] = otp
    request.session["account_change_time"] = timezone.now().timestamp()

    response = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(
            os.environ["MAILJET_API_KEY"],
            os.environ["MAILJET_SECRET_KEY"],
        ),
        json={
            "Messages": [
                {
                    "From": {
                        "Email": "smartcomputerins2022@gmail.com",
                        "Name": "Smart Computer Institute",
                    },
                    "To": [
                        {
                            "Email": email,
                        }
                    ],
                    "Subject": "Account Change Verification | Smart Computer Institute",
                    "TextPart": (
                        f"Dear User,\n\n"
                        f"Your account verification OTP is: {otp}\n\n"
                        f"This OTP is valid for 5 minutes.\n\n"
                        f"If you did not request this, please ignore this email.\n\n"
                        f"Regards,\n"
                        f"Smart Computer Institute"
                    ),
                }
            ]
        },
        timeout=30,
    )

    response.raise_for_status()

    return JsonResponse({"status": "sent"})

@login_required
def verify_account_change(request):

    otp = request.POST.get("otp")
    new_username = request.POST.get("username")
    new_password = request.POST.get("password")

    session_otp = request.session.get("account_change_otp")
    otp_time = request.session.get("account_change_time")

    if not session_otp:
        return JsonResponse({"status": "expired"})

    # OTP expires after 5 minutes
    if timezone.now().timestamp() - otp_time > 300:
        return JsonResponse({"status": "expired"})

    if otp != session_otp:
        return JsonResponse({"status": "invalid_otp"})

    user = request.user

    if new_username:
        user.username = new_username

    if new_password:
        user.set_password(new_password)

    user.save()

    from django.contrib.auth import logout  # ensure imported

    user.save()

    # 🔥 LOGOUT HERE
    logout(request)

    request.session.pop("account_change_otp", None)
    request.session.pop("account_change_time", None)

    return JsonResponse({
        "status": "success",
        "message": "Updated successfully! Please login again."
    })

from django.contrib.auth import logout
from django.urls import reverse

def logout_restricted(request):
    logout(request)
    request.session.flush()
    return redirect("/admin/login/")


def check_restriction(request):

    if not request.user.is_authenticated:
        return JsonResponse(
            {"restricted": True, "auth": False},
            status=401
        )

    cache_key = f"franchise_restricted_{request.user.id}"

    restricted = cache.get(cache_key)

    if restricted is None:
        from franchise.models import Franchise

        franchise = Franchise.objects.filter(
            user=request.user
        ).first()

        restricted = (
            franchise.is_restricted
            if franchise
            else False
        )

        cache.set(cache_key, restricted, 60)

    return JsonResponse({
        "restricted": restricted
    })

from django.contrib.auth.decorators import login_required

@login_required
def restricted_page(request):
    franchise = Franchise.objects.filter(user=request.user).first()

    return render(
        request,
        "franchise/restricted.html",
        {"manager_name": franchise.manager_name if franchise else ""}
    )