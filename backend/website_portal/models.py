
from django.db import models
from django.core.exceptions import ValidationError

class WebsiteExam(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Website Exam"
        verbose_name_plural = "Website Exams"


class WebsiteCourse(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    course_image = models.ImageField(
        upload_to="course_images/",
        blank=True,
        null=True
    )
    duration = models.PositiveIntegerField(
        help_text="Duration in months"
    )
    admission_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    show_on_homepage = models.BooleanField(
        default=False,
        verbose_name="Show on Popular Courses"
    )
    syllabus = models.TextField(blank=True)
    exams = models.ManyToManyField(
        WebsiteExam,
        blank=True
    )


    def clean(self):
        super().clean()

        if self.show_on_homepage and not self.course_image:
            raise ValidationError(
                "Course image is required when 'Show on Popular Courses' is enabled."
            )
        
    def __str__(self):
        return self.code

    class Meta:
        ordering = ["order"]
        verbose_name = "Website Course"
        verbose_name_plural = "Website Courses"

class Gallery(models.Model):
    title = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to="gallery/"
    )

    featured = models.BooleanField(
        default=False
    )

    order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery"

    def __str__(self):
        return self.title


class WhyChooseUs(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Why Choose Us"
        verbose_name_plural = "Why Choose Us"



class WebsiteContact(models.Model):
    institution_name = models.CharField(max_length=255, default="Smart Computer Institute")
    address = models.TextField(help_text="Full physical address of the institute")
    phone_number_1 = models.CharField(
        max_length=20,
        verbose_name="Phone Number 1"
    )

    phone_number_2 = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Phone Number 2"
    )

    phone_number_3 = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Phone Number 3"
    )
    email_address = models.EmailField(max_length=254, help_text="Official administrative email address")
    whatsapp_number_1 = models.CharField(
        max_length=20,
        verbose_name="WhatsApp Number 1"
    )

    whatsapp_number_2 = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="WhatsApp Number 2"
    )
    google_maps_link = models.URLField(
        max_length=500, 
        blank=True, 
        null=True, 
        help_text="Paste the Google Maps share link here"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Website Contact Information"
        verbose_name_plural = "Website Contact Information"

    def __str__(self):
        return f"{self.institution_name} - Contact Config"
    

class WebsiteStat(models.Model):
    number = models.CharField(
        max_length=20,
        help_text="Example: 1000+, 98%, 10+"
    )

    title = models.CharField(
        max_length=100,
        help_text="Example: Students, Courses"
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Website Statistic"
        verbose_name_plural = "Website Statistics"

    def __str__(self):
        return self.title
    

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    review = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    course = models.CharField(max_length=100, blank=True)
    place = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: Google Review"
    )
    order = models.PositiveIntegerField(default=0)
    show_on_homepage = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
    def __str__(self):
        return self.name