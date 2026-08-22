import threading
from django.db import connections

def send_certificate_email_async(instance_id, franchise):
    def run():
        from student_portal.models import Certificate
        from student_portal.utils.certificate_email import send_certificate_email
        from core.middleware import set_current_franchise

        # 🔥 restore tenant context
        set_current_franchise(franchise)

        # 🔥 fresh DB connection
        connections.close_all()

        print(f"🚀 THREAD STARTED for Certificate ID: {instance_id}")

        try:
            cert = Certificate.objects.get(pk=instance_id)


            print(f"📨 Sending email for ID {instance_id}")
            send_certificate_email(cert)

            # Mark email as sent only after successful sending
            cert.email_sent = True
            cert.save(update_fields=["email_sent"])
            print(f"✅ email_sent=True saved for Certificate ID: {instance_id}")

        except Certificate.DoesNotExist:
            print(f"❌ Certificate not found in DB: {instance_id}")

        except Exception as e:
            print(f"❌ THREAD ERROR: {e}")

    threading.Thread(target=run, daemon=True).start()