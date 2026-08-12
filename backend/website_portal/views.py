from django.http import JsonResponse
from .models import WebsiteCourse
from .models import WebsiteStat
from .models import WebsiteContact
from .models import WhyChooseUs
from .models import WebsiteContact
from .models import Testimonial
from .models import Gallery

def website_courses(request):

    courses = WebsiteCourse.objects.all().order_by("order")

    data = []

    for course in courses:
        data.append({
            "code": course.code,
            "name": course.name,
            "duration": course.duration,
            "admission_fee": course.admission_fee,
            "monthly_fee": course.monthly_fee,
            "course_image": (
                course.course_image.url
                if course.course_image
                else None
            ),
        })

    return JsonResponse(data, safe=False)

def popular_courses(request):

    courses = WebsiteCourse.objects.filter(
        show_on_homepage=True
    ).order_by("order")

    data = []

    for course in courses:
        data.append({
            "code": course.code,
            "name": course.name,
            "duration": course.duration,
            "admission_fee": course.admission_fee,
            "monthly_fee": course.monthly_fee,
            "course_image": (
                course.course_image.url
                if course.course_image
                else None
            ),
        })

    return JsonResponse(data, safe=False)




def website_course_detail(request, code):

    try:
        course = WebsiteCourse.objects.get(
            code__iexact=code.strip()
        )

        return JsonResponse({
            "id": course.id,
            "code": course.code,
            "name": course.name,
            "duration": course.duration,
            "admission_fee": course.admission_fee,
            "monthly_fee": course.monthly_fee,
            "syllabus": course.syllabus,
            "exams": [
                exam.name
                for exam in course.exams.all()
            ]
        })

    except WebsiteCourse.DoesNotExist:

        return JsonResponse(
            {
                "error": "Course not found"
            },
            status=404
        )
    

def website_contact(request):

    contact = WebsiteContact.objects.first()

    if not contact:
        return JsonResponse(
            {
                "error": "Contact information not configured"
            },
            status=404
        )

    return JsonResponse({

        "institution_name":
            contact.institution_name,

        "address":
            contact.address,

        "google_maps_link":  # ⚡ ADD THIS EXACT LINE HERE
            contact.google_maps_link,

        "phone_number_1":
            contact.phone_number_1,

        "phone_number_2":
            contact.phone_number_2,

        "phone_number_3":
            contact.phone_number_3,

        "email_address":
            contact.email_address,

        "whatsapp_number_1":
            contact.whatsapp_number_1,

        "whatsapp_number_2":
            contact.whatsapp_number_2,

    })






def website_stats(request):

    stats = WebsiteStat.objects.all()

    data = []

    for stat in stats:
        data.append({
            "number": stat.number,
            "title": stat.title,
        })

    return JsonResponse(data, safe=False)



def why_choose_us(request):

    items = WhyChooseUs.objects.all()

    data = []

    for item in items:
        data.append({
            "id": item.id,
            "title": item.title,
            "body": item.body,
        })

    return JsonResponse(data, safe=False)




def testimonials(request):

    reviews = Testimonial.objects.filter(
        show_on_homepage=True
    )

    data = []

    for review in reviews:

        data.append({
            "id": review.id,
            "name": review.name,
            "review": review.review,
            "rating": review.rating,
            "course": review.course,
            "place": review.place,
        })

    return JsonResponse(
        data,
        safe=False
    )




def gallery_images(request):

    images = Gallery.objects.filter(
        featured=True
    )

    data = []

    for image in images:

        data.append({
            "id": image.id,
            "title": image.title,
            "image": image.image.url,
        })

    return JsonResponse(
        data,
        safe=False
    )