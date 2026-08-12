from django.urls import path
from . import views

urlpatterns = [
    path(
        "create-lead/",
        views.create_lead,
        name="create_lead",
    ),
]