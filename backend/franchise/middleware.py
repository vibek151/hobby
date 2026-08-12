from django.shortcuts import redirect
from .models import Franchise


class ForcePasswordChangeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ✅ Skip middleware for reset + login flows ALWAYS
        if request.path.startswith((
            "/reset/",
            "/password_reset/",
            "/admin/password_reset/",
            "/admin/login/",
        )):
            return self.get_response(request)

        # ✅ Only check for fully authenticated users
        if request.user.is_authenticated and request.user.is_active:

            try:
                franchise = Franchise.objects.get(user=request.user)

                if franchise.force_password_change:

                    # Allow only these pages
                    if not request.path.startswith((
                        "/franchise/force-reset/",
                        "/logout/",
                    )):
                        return redirect("force_reset")

            except Franchise.DoesNotExist:
                pass

        return self.get_response(request)