from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.apps import apps

class MyAdminSite(AdminSite):
    site_header = ""  # 🔴 remove header text completely
    site_title = "Institute ERP"
    index_title = "Administration"

    def each_context(self, request):
        context = super().each_context(request)
        context["site_header"] = ""   # 🔥 force override in template
        return context

my_admin_site = MyAdminSite()

# Register auth models
my_admin_site.register(User)
my_admin_site.register(Group)

# Auto register all models safely
for model in apps.get_models():
    try:
        my_admin_site.register(model)
    except:
        pass