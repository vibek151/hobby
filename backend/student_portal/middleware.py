# from .reminders import run_fee_reminders
# from management_portal.scheduler import run_scheduled_notices
# class ReminderMiddleware:

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):

#         print("Reminder middleware triggered")

#         try:
#             run_fee_reminders()
#             run_scheduled_notices() 
#         except Exception as e:
#             print("Reminder error:", e)

#         response = self.get_response(request)

#         return response

from django.core.management import call_command

from management_portal.scheduler import run_scheduled_notices


class ReminderMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Run automated emails only when cron-job.org
        # calls the dedicated trigger URL.
        if request.path == "/fee-reminder-trigger/":

            print("Reminder middleware triggered")

            try:
                # This is the actual Mailjet-based fee + birthday command
                call_command("send_fee_reminders")

                # Keep scheduled notices working
                run_scheduled_notices()

                print("Reminder automation completed")

            except Exception as e:
                print("Reminder automation error:", e)

        response = self.get_response(request)

        return response