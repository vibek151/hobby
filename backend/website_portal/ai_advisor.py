import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import WebsiteCourse, WebsiteContact

@csrf_exempt
def ai_advisor_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        body = json.loads(request.body)
        # Accept code choices directly passed down from the button interaction
        choice = body.get("message", "").strip()
        
        courses = list(WebsiteCourse.objects.all())
        contact = WebsiteContact.objects.first()

        # --- CHOICE 1: AVAILABLE COURSES ---
        if choice == "1":
            reply = "🎓 **Our Certified Academic Programs:**\n\n"
            if courses:
                for i, c in enumerate(courses, 1):
                    reply += f"{i}. **{c.name}** — Course Module Duration: {c.duration} Months\n"
            else:
                reply += "• Professional Software Development\n• Diploma in Computing & Office Applications (DCOA)\n• Accounting Modules\n"
            reply += "\nClick the 'Check Fees' button below to see the exact breakdown for these programs!"
            return JsonResponse({"reply": reply})

        # --- CHOICE 2: ADMISSION & MONTHLY FEES ---
        elif choice == "2":
            reply = "💰 **Official Institute Fee Structure:**\n\n"
            if courses:
                for c in courses:
                    reply += f"• **{c.name}**\n  - Admission Registration: ₹{getattr(c, 'admission_fee', 'N/A')}\n  - Monthly Installment: ₹{getattr(c, 'monthly_fee', 'N/A')}\n\n"
            else:
                reply += "Our standard courses feature flexible admission models with basic monthly installment programs.\n"
            return JsonResponse({"reply": reply})

        # --- CHOICE 3: BATCH SCHEDULES & TIMINGS ---
        elif choice == "3":
            reply = "📅 **Online Live Class Schedules:**\n\n" \
                    "• **Working Days:** Monday to Saturday\n" \
                    "• **Daily Working Hours:** 8:00 AM to 7:00 PM\n" \
                    "• **Weekly Holiday:** Sundays (Closed)\n\n" \
                    "Classes run in flexible morning, afternoon, and evening batches to fit your free hours comfortably."
            return JsonResponse({"reply": reply})

        # --- CHOICE 4: SYSTEM & APP REQUIREMENTS ---
        elif choice == "4":
            reply = "💻 **Pre-requisites for Attending Online Classes:**\n\n" \
                    "1. **Device:** A laptop, desktop system, or tablet screen.\n" \
                    "2. **Internet:** Stable connection for high-resolution desk sharing.\n" \
                    "3. **Software Setup:** An operating system capable of running standard terminal environments, office software suites, or development engines."
            return JsonResponse({"reply": reply})

        # --- CHOICE 5: CERTIFICATE AND ISO ACCREDITATION ---
        elif choice == "5":
            reply = "📜 **Accreditation & Final Certification:**\n\n" \
                    "• Upon completing the core modules and turning in your final lab assignments, you will be awarded an official institute **Certified Diploma**.\n" \
                    "• Our certifications carry professional corporate validity for job listings, document processing, and freelance tracking data profiles."
            return JsonResponse({"reply": reply})

        # --- CHOICE 6: HOW TO ENROLL / CONTACTS ---
        elif choice == "6":
            addr = contact.address if contact else "Champasari Main Road, Siliguri, West Bengal"
            ph = contact.phone_numbers if contact else "our support office desk"
            whatsapp = getattr(contact, 'whatsapp_number', ph)
            
            reply = f"📞 **Complete Enrollment Registration Guidelines:**\n\n" \
                    f"• **Step 1:** Select your preferred training track module.\n" \
                    f"• **Step 2:** Provide 2 copies of passport size photos and your final qualification marksheets.\n\n" \
                    f"📍 **Office Center Desk Address:** {addr}\n" \
                    f"☎️ **Contact Helpline:** {ph}\n" \
                    f"🟢 **WhatsApp Support Line:** {whatsapp}"
            return JsonResponse({"reply": reply})

        # --- DEFAULT RESTORE BACKUP ---
        return JsonResponse({
            "reply": "Welcome to Smart Institute! Please use one of the quick clickable menu buttons below to find instantly verified details regarding fees, modules, or registration links."
        })

    except Exception:
        return JsonResponse({"reply": "The lookup service is refreshing. Please tap the button again in a moment!"})