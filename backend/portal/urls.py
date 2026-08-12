"""
URL configuration for portal app
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('apply/', views.AdmissionView.as_view(), name='admission'),
    path('apply/success/', views.AdmissionSuccessView.as_view(), name='admission_success'),
    path('courses/', views.CoursesView.as_view(), name='courses'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]
