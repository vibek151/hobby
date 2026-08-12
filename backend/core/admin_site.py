from django.contrib.admin import AdminSite
from django.contrib import messages


class MyAdminSite(AdminSite):

    site_header = "Smart Computer Institute Admin"
    site_title = "Admin Panel"
    index_title = "Site Administration"

    def login(
        self,
        request,
        extra_context=None
    ):

        response = super().login(
            request,
            extra_context
        )

        # login message
        if (
            request.method == "POST"
            and request.user.is_authenticated
        ):

            messages.success(
                request,
                f"Login successful. Welcome, "
                f"{request.user.username}!"
            )

        return response

    # ================= SIDEBAR CONTROL =================

    def get_app_list(
        self,
        request,
        app_label=None
    ):

        app_list = super().get_app_list(
            request,
            app_label
        )

        # franchise login only
        if (
            request.user.is_staff
            and not request.user.is_superuser
        ):

            for app in app_list:

                filtered_models = []

                for model in app["models"]:

                    # remove only Franchises
                    if (
                        model.get(
                            "object_name"
                        ) == "Franchise"
                    ):
                        continue

                    filtered_models.append(
                        model
                    )

                app["models"] = (
                    filtered_models
                )

        return app_list


admin_site = MyAdminSite()