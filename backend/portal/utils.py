from twilio.rest import Client
from django.conf import settings

def send_whatsapp_otp(phone, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        body=f"Your Smart Computer Institute OTP is: {otp}",
        from_=settings.TWILIO_WHATSAPP_NUMBER,
        to=f"whatsapp:{phone}"
    )

    return message.sid


import random
from .models import DeleteOTP

def generate_delete_otp(user, phone):
    otp = str(random.randint(100000, 999999))
    DeleteOTP.objects.create(user=user, otp=otp)
    send_whatsapp_otp(phone, otp)
    return otp
