import threading
from django.shortcuts import redirect
from django.urls import reverse, resolve

_thread_locals = threading.local()


# ===============================
# 🔹 GETTERS (USED BY MODELS)
# ===============================
def get_current_franchise():
    return getattr(_thread_locals, "franchise", None)


def get_current_user():
    return getattr(_thread_locals, "user", None)

def set_current_franchise(franchise):
    _thread_locals.franchise = franchise


# ===============================
# 🔹 TENANT MIDDLEWARE
# ===============================
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # 🔥 Always reset first (important)
        _thread_locals.franchise = None
        _thread_locals.user = request.user

        if request.user.is_authenticated:

            if request.user.is_superuser:
                return self.get_response(request)

            from franchise.models import Franchise

            franchise = Franchise.objects.filter(user=request.user).first()
            _thread_locals.franchise = franchise

            # ===============================
            # 🔒 RESTRICTION LOGIC
            # ===============================
            if request.path == "/franchise/check-restriction/":
                return self.get_response(request)
            if franchise and franchise.is_restricted:

                try:
                    current_url_name = resolve(request.path_info).url_name
                except:
                    current_url_name = None

                # ✅ Allowed routes (no redirect)
                exempt_names = [
                    "restricted_page",
                    "logout",
                    "login",
                    "password_reset",
                    "password_reset_done",
                    "password_reset_confirm",
                    "password_reset_complete",
                ]

                exempt_prefixes = [
                    "/static/",
                    "/media/",
                    "/admin/login/",
                    "/admin/password_reset/",
                    "/franchise/restricted/",
                ]

                is_exempt = (
                    current_url_name in exempt_names
                    or any(request.path.startswith(p) for p in exempt_prefixes)
                )

                # 🚫 Redirect if not allowed
                if not is_exempt:
                    try:
                        return redirect(reverse("restricted_page"))
                    except:
                        return redirect("/franchise/restricted/")

        return self.get_response(request)