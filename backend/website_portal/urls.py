from django.urls import path
from . import views
from . import ai_advisor
from .views import website_stats
urlpatterns = [

    path(
        "courses/",
        views.website_courses,
        name="website_courses"
    ),

    path(
        "courses/<str:code>/",
        views.website_course_detail,
        name="website_course_detail"
    ),
    path(
        "popular-courses/",
        views.popular_courses,
        name="popular_courses"
    ),
    path(
        "contact/",
        views.website_contact,
        name="website_contact"
    ),
    path('ai-advisor/', ai_advisor.ai_advisor_view, name='ai-advisor'),
    path(
        "stats/",
        website_stats,
        name="website_stats"
    ),
    path(
        "why-choose-us/",
        views.why_choose_us,
        name="why_choose_us"
    ),
    path(
        "testimonials/",
        views.testimonials,
        name="testimonials"
    ),
    path(
        "gallery/",
        views.gallery_images,
        name="gallery_images"
    ),
    path(
        "sitemap.xml",
        views.website_sitemap,
        name="website_sitemap"
    ),
]