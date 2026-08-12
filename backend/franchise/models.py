from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver



class Franchise(models.Model):
    # Link to the User account for login
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    manager_name = models.CharField(max_length=200)
    
    # Non-unique so one person can have multiple branches with the same name
    institute_name = models.CharField(max_length=200)

    institute_location = models.TextField()


    reset_code = models.CharField(max_length=8, null=True, blank=True)
    reset_code_expiry = models.DateTimeField(null=True, blank=True)

    reset_otp = models.CharField(max_length=8, null=True, blank=True)
    reset_otp_expiry = models.DateTimeField(null=True, blank=True)

    reset_lock_until = models.DateTimeField(null=True, blank=True)
    reset_attempts = models.IntegerField(default=0)
    force_password_change = models.BooleanField(default=False)


    passport_photo = models.ImageField(
        upload_to="franchise/passport/",
        null=True,
        blank=True
    )

    id_proof_number = models.CharField(max_length=100)

    id_proof_file = models.FileField(
        upload_to="franchise/idproof/",
        null=True,
        blank=True
    )
    signature = models.ImageField(
        upload_to="franchise/signature/",
        null=True,
        blank=False
    )
    trade_license_number = models.CharField(
        max_length=100,
        unique=True
    )
    email = models.EmailField(blank=True, null=True)


    student_id_part1 = models.CharField(max_length=10, default="MG")
    student_id_part2 = models.CharField(max_length=10, default="SLG")
    student_id_part3 = models.CharField(max_length=10)
    email_verified = models.BooleanField(default=False)
    is_restricted = models.BooleanField(default=False)

    # 👇 ADD THIS METHOD HERE
    def signature_preview(self):
        if self.signature:
            return format_html(
                '<img src="{}" width="120" style="border:1px solid #ccc;" />',
                self.signature.url
            )
        return "No Signature"

    signature_preview.short_description = "Signature Preview"


    # --- THE UPDATE FOR CAPITALIZATION ---
    def save(self, *args, **kwargs):
        """
        Custom save method to ensure manager_name is always 
        Capitalized Each Word before saving to the database.
        """
        if self.manager_name:
            # .strip() removes accidental spaces, .title() capitalizes each word
            self.manager_name = self.manager_name.strip().title()
        
        super(Franchise, self).save(*args, **kwargs)

        # ================= SIGNATURE RESIZE =================
        if self.signature:
            try:
                img_path = self.signature.path

                if os.path.exists(img_path):
                    img = Image.open(img_path)

                    # 🔥 BEST METHOD (no distortion)
                    img.thumbnail((300, 100))

                    img.save(img_path)

            except Exception as e:
                print("Signature resize error:", e)

    def __str__(self):
        # Updated string representation for better visibility in Admin
        return f"{self.institute_name} - {self.institute_location} ({self.manager_name})"
    
class FranchiseAccount(models.Model):

    franchise = models.OneToOneField(
        "Franchise",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Access Portal"
        verbose_name_plural = "Access Portal"

    def __str__(self):
        return self.franchise.institute_name
    
@receiver(post_save, sender=Franchise)
def create_access_portal(sender, instance, created, **kwargs):
    if created:
        FranchiseAccount.objects.create(franchise=instance)

