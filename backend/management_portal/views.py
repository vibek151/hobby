from django.shortcuts import render

# Create your views here.
# management_portal/views.py (Example)
from core.db_mongo import mongodb

def save_activity(request):
    # This reaches through the 'Wall' to the shared MongoDB
    log_collection = mongodb["activity_logs"]
    log_collection.insert_one({
        "franchise": request.user.username,
        "action": "Checked Dashboard",
        "time": "2026-04-22"
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import Lead
from website_portal.models import WebsiteCourse


@csrf_exempt
@require_POST
def create_lead(request):
    try:
        data = json.loads(request.body)

        print("REQUEST DATA:", data)

        course_id = data.get("course")
        print("COURSE ID:", course_id)

        course = WebsiteCourse.objects.filter(id=course_id).first()
        print("COURSE OBJECT:", course)

        Lead.objects.create(
            name=data.get("name"),
            phone=data.get("phone"),
            email=data.get("email", ""),
            qualification=data.get("qualification", ""),
            course=course,
            message=data.get("message", ""),
        )

        return JsonResponse({
            "success": True,
            "message": "Application submitted successfully."
        })

    except Exception as e:
        print(e)
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=400)