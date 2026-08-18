from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import os
from django.conf import settings
from datetime import datetime
from PIL import Image

from student_portal.models import StudentAdmission, Certificate


# 🔥 KEEP YOUR EXISTING HELPER (must already exist in your project)
def draw_wrapped_text(p, text, x, y, max_width):
    from reportlab.pdfbase.pdfmetrics import stringWidth

    words = text.split()
    line = ""

    for word in words:
        test_line = f"{line} {word}".strip()
        if stringWidth(test_line, "Helvetica", 11) < max_width:
            line = test_line
        else:
            p.drawString(x, y, line)
            y -= 15
            line = word

    if line:
        p.drawString(x, y, line)
        y -= 15

    return y


def generate_admission_pdf(student):

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    page_number = 1

    # Logo & Branding
    logo_path = os.path.join(settings.BASE_DIR, "student_portal/static/logo.jpg")
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 40, height-90, width=70, height=70)

    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2 + 33, height-40, "SMART COMPUTER INSTITUTE")

    p.setFont("Helvetica", 11)
    p.drawCentredString(width-157, height-60, "Build Skills, Build Futures.....")

    p.line(120, height-80, 550, height-80)

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height-100, "ADMISSION FORM")

    # Watermark
    if os.path.exists(logo_path):
        p.saveState()
        p.setFillAlpha(0.1)
        p.drawImage(
            logo_path,
            (width - 300) / 2,
            (height - 300) / 2 + 50,
            width=300,
            height=300,
            mask='auto',
            preserveAspectRatio=True
        )
        p.restoreState()

    # Passport Photo
    if student.passport_photo:
        try:
            p.rect(width - 155, height - 240, 100, 120)
            p.drawImage(
                student.passport_photo.path,
                width - 155,
                height - 240,
                width=100,
                height=120
            )
        except Exception as e:
            print("Passport photo error:", e)

    y = height-145

    # PERSONAL DETAILS
    p.setFont("Helvetica-Bold", 13)
    p.drawString(40, y, "PERSONAL DETAILS")
    y -= 20

    p.setFont("Helvetica", 11)

    details = [
        f"Student ID : {student.student_id}",
        f"Name : {student.name}",
        f"Guardian Name : {getattr(student, 'guardian_name', '-')}",
        f"DOB : {getattr(student, 'dob', '-')}",
        f"Phone : {student.phone}",
        f"Email : {student.email}",
        f"Qualification : {getattr(student, 'qualification', '-')}",
        f"Gender : {getattr(student, 'gender', '-')}",
        f"Admission Date : {student.admission_date.strftime('%d-%m-%Y') if student.admission_date else '-'}",
        f"Document No.:{getattr(student, 'document_number', '-')}",
        f"Address : {getattr(student, 'address', '-')}",
    ]

    for line in details:
        y = draw_wrapped_text(p, line, 50, y, 450)

    # PREVIOUS COURSE
    prev_course = None
    previous_admissions = StudentAdmission.objects.filter(
        student_id=student.student_id
    ).exclude(id=student.id)

    for admission in previous_admissions:
        if admission.course_completed:
            prev_course = admission
            break

    if prev_course:
        y -= 10
        p.setFont("Helvetica-Bold", 13)
        p.drawString(40, y, "PREVIOUS COURSE RECORD")
        y -= 20

        p.setFont("Helvetica", 11)

        cert = Certificate.objects.filter(
            enrollment__student=prev_course
        ).first()

        p.drawString(50, y, f"Course: {prev_course.course}")
        y -= 18

        p.drawString(50, y, f"Certificate No: {getattr(cert, 'certificate_no', 'N/A')}")
        y -= 18

        p.drawString(50, y, f"Marksheet No: {getattr(cert, 'marksheet_no', 'N/A')}")
        y -= 25

    # COURSE DETAILS
    y -= 10
    p.setFont("Helvetica-Bold", 13)
    p.drawString(40, y, "COURSE DETAILS")
    y -= 20

    p.setFont("Helvetica", 11)

    try:
        days = ", ".join([d.day for d in student.class_day.all()]) or "-"
    except:
        days = "-"

    c_info = [
        f"Course : {student.course}",
        f"Type : {getattr(student, 'course_type', '-')}",
        f"Duration : {getattr(student, 'course_duration', '-')} Months",
        f"Batch Days : {days}",
        f"Batch Time : {getattr(student, 'class_time', '-')}"
    ]

    for line in c_info:
        p.drawString(50, y, line)
        y -= 18

    # PAYMENT DETAILS
    y -= 10
    p.setFont("Helvetica-Bold", 13)
    p.drawString(40, y, "PAYMENT DETAILS")
    y -= 20

    p.setFont("Helvetica", 11)

    p_info = [
        f"Receipt No : {getattr(student, 'receipt_no', '-')}",
        f"Admission Fee : Rs. {getattr(student, 'admission_amount', '-')}",
        f"Discount (%) : {getattr(student, 'discount_percent', '-')}",
        f"Final Amount : Rs. {getattr(student, 'final_amount', '-')}",
        f"Monthly Fee : Rs. {getattr(student, 'monthly_fee', '-')}"
    ]

    for line in p_info:
        p.drawString(50, y, line)
        y -= 18

    # RULES
    y -= 10
    p.setFont("Helvetica-Bold", 13)
    p.drawString(40, y, "RULES & REGULATIONS")
    y -= 20

    p.setFont("Helvetica", 10)

    rules = [
        "1. Student ID card must be carried during class.",
        "2. Arrive on time; repeated lateness affects attendance.",
        "3. Study materials are for personal use only.",
        "4. Inform the office before taking long leave.",
        "5. Institute may revise rules and enforce discipline."
    ]

    for rule in rules:
        p.drawString(50, y, rule)
        y -= 15

    # SIGNATURE
    signature_path = None
    franchise = getattr(student, "franchise", None)

    if franchise and franchise.signature:
        try:
            signature_path = franchise.signature.path
        except:
            signature_path = None

    if signature_path and os.path.exists(signature_path):
        try:
            signature_width = 150
            signature_height = 50

            signature_x = width - 190
            signature_y = 65

            p.drawImage(
                signature_path,
                signature_x,
                signature_y,
                width=signature_width,
                height=signature_height,
                mask="auto",
            )

        except Exception as e:
            print("Signature draw error:", e)

    # FOOTER
    p.line(width - 200, 65, width - 50, 65)
    p.setFont("Helvetica-Oblique", 11)
    p.drawRightString(width - 50, 55, "Authorized Signatory")

    timestamp = datetime.now().strftime("%d-%m-%Y | %I:%M %p")

    p.setFont("Helvetica", 9)
    p.drawString(40, 45, f"Generated on: {timestamp}")

    p.line(40, 35, 550, 35)

    p.setFont("Helvetica", 9)
    p.saveState()
    p.setFillAlpha(0.6)
    p.drawString(40, 25, "SMART COMPUTER INSTITUTE")
    p.restoreState()

    p.drawRightString(550, 25, f"Page | {page_number}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer