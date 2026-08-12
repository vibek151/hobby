from .reminders import run_fee_reminders
from management_portal.scheduler import run_scheduled_notices

# class ReminderMiddleware:

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):

#         try:
#             run_fee_reminders()
#         except:
#             pass

#         response = self.get_response(request)

#         return response

from .reminders import run_fee_reminders

class ReminderMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        print("Reminder middleware triggered")

        try:
            run_fee_reminders()
            run_scheduled_notices() 
        except Exception as e:
            print("Reminder error:", e)

        response = self.get_response(request)

        return response