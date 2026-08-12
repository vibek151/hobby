from dateutil.relativedelta import relativedelta
from student_portal.models import Fee, get_safe_date
from django.db.models import Sum
import calendar
import calendar
from dateutil.relativedelta import relativedelta


def calculate_due_date(admission_date, target_date):

    admission_day = admission_date.day

    months = (
        (target_date.year - admission_date.year) * 12
        + (target_date.month - admission_date.month)
    )

    cycle_date = admission_date + relativedelta(
        months=months
    )

    days_in_month = calendar.monthrange(
        cycle_date.year,
        cycle_date.month
    )[1]

    cycle_anchor = cycle_date.replace(
        day=min(
            admission_day,
            days_in_month
        )
    )

    grace_due = (
        cycle_anchor
        + relativedelta(days=5)
    )

    month_end = cycle_anchor.replace(
        day=days_in_month
    )

    return min(
        grace_due,
        month_end
    )
def calculate_due(cycle_date):

    tentative = (
        cycle_date
        + relativedelta(days=5)
    )

    last_day = calendar.monthrange(
        cycle_date.year,
        cycle_date.month
    )[1]

    month_end = cycle_date.replace(
        day=last_day
    )

    return min(
        tentative,
        month_end
    )

def calculate_student_dues(
    enrollment,
    payment_date
):
    print("******** FEE_ENGINE LOADED ********")
    admission_date = enrollment.admission_date
    admission_day = admission_date.day

    last_fee = (
        Fee._base_manager
        .filter(
            enrollment=enrollment,
            fee_type="MONTHLY"
        )
        .order_by("-id")
        .first()
    )

    old_fee_due = 0
    old_fine_due = 0

    if last_fee:
        old_fee_due = last_fee.remaining_fee or 0
        old_fine_due = last_fee.remaining_fine or 0

  
    # =====================
    # SAME DAY REOPEN
    # =====================

    if (
        last_fee
        and payment_date == last_fee.payment_date
    ):

        return {
            "amount": old_fee_due,
            "fine": old_fine_due,
            "due_date": last_fee.due_date,
            "pending_months": 0
        }

    # =====================
    # FULLY PAID HISTORY
    # =====================

    # if (
    #     last_fee
    #     and old_fee_due == 0
    # ):

    #     # still same month
    #     if months_diff == 0:
    #         print(
    #             "EARLY RETURN:",
    #             last_fee.due_date
    #         )
    #         return {
    #             "amount": 0,
    #             "fine": 0,
    #             "due_date": last_fee.due_date,
    #             "pending_months": 0
    #         }

    #     # new month cycle starts
    #     else:

    #         cycle = get_safe_date(
    #             payment_date.year,
    #             payment_date.month,
    #             admission_day
    #         )

    #         next_due = calculate_due(
    #             cycle
    #         )

    #         return {

    #             "amount": enrollment.monthly_fee,
    #             "fine": old_fine_due,
    #             "due_date": next_due,
    #             "pending_months": 1
    #         }

    # =====================
    # PENDING MONTHS
    # Calendar Month Logic
    # =====================

    first_payable_month = (
        admission_date
        + relativedelta(months=1)
    )

    if payment_date < first_payable_month.replace(day=1):

        pending_months = 0

    else:

        total_months_due = (
            (payment_date.year - first_payable_month.year) * 12
            + (payment_date.month - first_payable_month.month)
        ) + 1

        total_paid = (
            Fee._base_manager
            .filter(
                enrollment=enrollment,
                fee_type="MONTHLY"
            )
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        cleared_months = int(
            total_paid // enrollment.monthly_fee
        )

        pending_months = max(
            0,
            total_months_due - cleared_months
        )

    pending_months = max(
        0,
        pending_months
    )
    # no active dues at all
    if (
        pending_months <= 0
        and old_fee_due <= 0
        and old_fine_due <= 0
    ):

        return {
            "amount": 0,
            "fine": 0,
            "due_date": calculate_due(
                get_safe_date(
                    payment_date.year,
                    payment_date.month,
                    admission_day
                )
            ),
            "pending_months": 0
        }
    # =====================
    # COURSE LIMIT
    # =====================

    total_paid = (
        Fee._base_manager
        .filter(
            enrollment=enrollment,
            fee_type="MONTHLY"
        )
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )

    remaining_course_fee = max(
        0,
        enrollment.total_fee - total_paid
    )
    # =====================================
    # ACTIVE MONTHLY DUES
    # =====================================

    if old_fee_due > 0:

        amount = min(
            old_fee_due +
            (
                enrollment.monthly_fee
                * max(0, pending_months - 1)
            ),
            old_fee_due + remaining_course_fee
        )

    else:
        current_fee = (
            enrollment.monthly_fee
            * pending_months
        )

        amount = min(
            current_fee,
            remaining_course_fee
        )

    # =====================
    # FINE CALCULATION
    # =====================

    fine = old_fine_due or 0

    # =====================================
    # CASE 1
    # FEE STILL UNPAID
    # Fine keeps increasing daily
    # =====================================

    if old_fee_due > 0 and last_fee:

        fine_start = last_fee.due_date + relativedelta(days=1)

        if payment_date >= fine_start:

            extra_days = (
                payment_date - fine_start
            ).days + 1

            fine = extra_days * 5

    # =====================================
    # CASE 2
    # FEE FULLY CLEARED
    # Freeze fine
    # =====================================

    elif old_fine_due > 0 and last_fee:

        fine = old_fine_due

        # next month's due date
        next_due_date = calculate_due(
            get_safe_date(
                payment_date.year,
                payment_date.month,
                admission_day
            )
        )

        restart_date = (
            next_due_date
            + relativedelta(days=1)
        )

        if payment_date >= restart_date:

            extra_days = (
                payment_date - restart_date
            ).days + 1

            fine = old_fine_due + (
                extra_days * 5
            )

    # =====================================
    # CASE 3
    # FIRST OVERDUE EVER
    # =====================================

    else:

        first_payable = (
            admission_date
            + relativedelta(months=1)
        )

        first_due = calculate_due_date(
            admission_date,
            first_payable
        )

        fine_start = (
            first_due
            + relativedelta(days=1)
        )

        if payment_date >= fine_start:

            days = (
                payment_date - fine_start
            ).days + 1

            fine = days * 5
    # =====================
    # DISPLAY DUE DATE
    # =====================

    import calendar

    # current active cycle month
    cycle_month = get_safe_date(
        payment_date.year,
        payment_date.month,
        admission_day
    )

    cycle_anchor = cycle_month

    tentative_due = (
        cycle_anchor
        + relativedelta(days=5)
    )

    last_day = calendar.monthrange(
        cycle_month.year,
        cycle_month.month
    )[1]

    month_end = cycle_month.replace(
        day=last_day
    )

    due_date = calculate_due(cycle_anchor)
    print("cycle_anchor:", cycle_anchor)
    print("pending:", pending_months)
    print("due:", due_date)
    print("================================")
    print("PAYMENT DATE =", payment_date)
    print("PENDING MONTHS =", pending_months)
    print("OLD FEE DUE =", old_fee_due)
    print("AMOUNT =", amount)
    print("FINE =", fine)
    print("================================")

    print("================================")
    print("DEBUG")
    print("old_fee_due =", old_fee_due)
    print("old_fine_due =", old_fine_due)

    if last_fee:
        print("last_fee.id =", last_fee.id)
        print("last_fee.remaining_fee =", last_fee.remaining_fee)
        print("last_fee.remaining_fine =", last_fee.remaining_fine)

    print("FINAL AMOUNT =", amount)
    print("FINAL FINE =", fine)

    print(
        "remaining_course_fee =", remaining_course_fee,
        "| old_fee_due =", old_fee_due,
        "| pending_months =", pending_months,
        "| amount =", amount
    )

    print("================================")

    return {
        "amount": amount,
        "fine": fine,
        "due_date": due_date,
        "pending_months": pending_months
    }