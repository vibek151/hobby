# from django.shortcuts import render
# from django.contrib.auth.models import User
# from django.core.mail import send_mail
# from franchise.models import Franchise
# from django.contrib.auth.views import LoginView
# from django.contrib import messages

# import os
# import requests
# # ===============================
# # NORMAL VIEWS (UNCHANGED)
# # ===============================

# def dashboard(request):
#     return render(request, "student_portal/dashboard.html")


# def payments(request):
#     return render(request, "student_portal/payments.html")


# def pay(request):
#     return render(request, "student_portal/pay.html")





# from django.core.mail import send_mail
# from django.shortcuts import render

# from django.http import HttpResponse

# def health_check(request):
#     return HttpResponse("OK")


# def forgot_username(request):
#     message = ""

#     if request.method == "POST":
#         email = request.POST.get("email")
#         user = User.objects.filter(email=email).first()

#         if not user:
#             franchise = Franchise.objects.filter(email=email).first()

#             if franchise:
#                 user = franchise.user

#         if user:

#             html_content = f"""
#             <!DOCTYPE html>
#             <html>
#             <head>
#                 <meta charset="utf-8">
#                 <meta name="viewport" content="width=device-width, initial-scale=1.0">
#                 <style>
#                     body {{
#                         font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
#                         background-color: #f9fafb;
#                         color: #1f2937;
#                         margin: 0;
#                         padding: 40px 20px;
#                     }}
#                     .container {{
#                         max-width: 480px;
#                         margin: 0 auto;
#                         background-color: #ffffff;
#                         padding: 32px;
#                         border-radius: 8px;
#                         border: 1px solid #e5e7eb;
#                         box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
#                     }}
#                     .header {{
#                         font-size: 13px;
#                         text-transform: uppercase;
#                         letter-spacing: 0.05em;
#                         color: #6b7280;
#                         margin-bottom: 24px;
#                         font-weight: 600;
#                     }}
#                     p {{
#                         font-size: 15px;
#                         line-height: 1.6;
#                         margin: 0 0 20px 0;
#                         color: #374151;
#                     }}
#                     .username-box {{
#                         background-color: #f3f4f6;
#                         border-radius: 6px;
#                         padding: 14px 16px;
#                         text-align: center;
#                         margin: 24px 0;
#                         border: 1px solid #e5e7eb;
#                     }}
#                     .username-label {{
#                         font-size: 11px;
#                         text-transform: uppercase;
#                         letter-spacing: 0.05em;
#                         color: #6b7280;
#                         margin-bottom: 4px;
#                         font-weight: 600;
#                     }}
#                     .username-text {{
#                         font-size: 18px;
#                         font-weight: 600;
#                         color: #111827;
#                         letter-spacing: 0.5px;
#                     }}
#                     .footer {{
#                         margin-top: 32px;
#                         padding-top: 20px;
#                         border-top: 1px solid #e5e7eb;
#                         font-size: 13px;
#                         color: #6b7280;
#                         line-height: 1.5;
#                     }}
#                 </style>
#             </head>
#             <body>
#                 <div class="container">
#                     <div class="header">Smart Computer Institute</div>
                    
#                     <p>Dear User,</p>
#                     <p>We received a request to recover the username associated with your account.</p>
                    
#                     <!-- Updated Username Box with explicit label -->
#                     <div class="username-box">
#                         <div class="username-label">Your Username</div>
#                         <div class="username-text">{user.username}</div>
#                     </div>
                    
#                     <p>If you did not request this recovery, you can safely ignore this email. No changes have been made to your account.</p>
                    
#                     <div class="footer">
#                         Regards,<br>
#                         <strong>Smart Computer Institute</strong><br>
#                         Administration Team
#                     </div>
#                 </div>
#             </body>
#             </html>
#             """

#             response = requests.post(
#                 "https://api.mailjet.com/v3.1/send",
#                 auth=(
#                     os.environ["MAILJET_API_KEY"],
#                     os.environ["MAILJET_SECRET_KEY"],
#                 ),
#                 json={
#                     "Messages": [
#                         {
#                             "From": {
#                                 "Email": "noreply@smartci.in",
#                                 "Name": "Smart Computer Institute",
#                             },
#                             "To": [
#                                 {
#                                     "Email": email,
#                                 }
#                             ],
#                             "Subject": "Account Username Recovery | Smart Computer Institute",
#                             "TextPart": (
#                                 f"Dear User,\n\n"
#                                 f"We received a request to recover the username for your "
#                                 f"Smart Computer Institute account.\n\n"
#                                 f"Your login username is: {user.username}\n\n"
#                                 f"If you did not request this recovery, you can safely "
#                                 f"ignore this email.\n\n"
#                                 f"Regards,\n"
#                                 f"Smart Computer Institute Team"
#                             ),
#                             "HTMLPart": html_content,
#                         }
#                     ]
#                 },
#                 timeout=30,
#             )

#             response.raise_for_status()

#             message = "Your username has been sent to your registered email address."
#         else:
#             message = "No account found with this email."

#     return render(request, "admin/forgot_username.html", {"message": message})


# # ===============================
# # ADMIN LOGIN SUCCESS MESSAGE
# # ===============================

# from django.contrib.auth.views import LoginView
# from django.contrib import messages
# from django.shortcuts import redirect
# from django.urls import reverse

# from django.shortcuts import redirect

# class CustomAdminLoginView(LoginView):
#     template_name = "admin/login.html"

#     def dispatch(self, request, *args, **kwargs):
#         # ✅ Only redirect if user is authenticated AND not already on admin index
#         if request.user.is_authenticated:
#             return redirect(reverse("admin:index"))
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         response = super().form_valid(form)

#         messages.success(
#             self.request,
#             f"Login successful. Welcome, {self.request.user.username}!"
#         )

#         return response


from django.http import HttpResponse
def forgot_username(request):
    return HttpResponse("FORGOT USERNAME VIEW IS WORKING")