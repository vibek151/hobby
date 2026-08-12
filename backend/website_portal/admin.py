from django.contrib import admin
from .models import WebsiteCourse, WebsiteExam, Gallery, WhyChooseUs
from django.utils.html import format_html
from .models import WebsiteContact
from .models import Testimonial
from .models import WebsiteStat


@admin.register(WebsiteExam)
class WebsiteExamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )
    search_fields = (
        "name",
    )


@admin.register(WebsiteCourse)
class WebsiteCourseAdmin(admin.ModelAdmin):
    list_display = (
         "order",
        "code",
        "name",
        "duration",
        "admission_fee",
        "monthly_fee",
        "show_on_homepage",
    )

    list_editable = (
        "order",
        "show_on_homepage",
    )
    list_display_links = (
        "code",
    )
    search_fields = (
        "code",
        "name",
    )

    filter_horizontal = (
        "exams",
    )



@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "card",
        "featured",
    )

    list_editable = (
        "order",
        "featured",
    )

    list_display_links = (
        "card",
    )

    actions = (
        "make_featured",
        "remove_featured",
    )

    def card(self, obj):
        return format_html(
            """
            <div style="
                width:220px;
                background:white;
                border-radius:12px;
                overflow:hidden;
                box-shadow:0 2px 10px rgba(0,0,0,.1);
                text-align:center;
            ">
                <img src="{}"
                     style="
                        width:100%;
                        height:130px;
                        object-fit:cover;
                     ">

                <div style="
                    padding:10px;
                    font-size:16px;
                    font-weight:600;
                ">
                    {}
                </div>
            </div>
            """,
            obj.image.url,
            obj.title
        )

    card.short_description = "Image"

    @admin.action(description="Mark selected images as featured")
    def make_featured(self, request, queryset):
        queryset.update(featured=True)



    @admin.action(description="Remove featured status")
    def remove_featured(self, request, queryset):
        queryset.update(featured=False)

    class Media:
        css = {
            "all": ("admin/gallery.css",)
        }
    
@admin.register(WhyChooseUs)
class WhyChooseUsAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "order",
    )

    list_editable = (
        "order",
    )

    search_fields = (
        "title",
    )





@admin.register(WebsiteContact)
class WebsiteContactAdmin(admin.ModelAdmin):

    list_display = (
        "institution_name",
        "phone_number_1",
        "email_address",
        "updated_at",
    )

    fieldsets = (

        (
            "Institute Information",
            {
                "fields": (
                    "institution_name",
                    "address",
                    "google_maps_link",  # ⚡ Added right below address
                ),
                "description": "Full physical address and location details of the institute."
            }
        ),

        (
            "Phone Numbers",
            {
                "fields": (
                    "phone_number_1",
                    "phone_number_2",
                    "phone_number_3",
                )
            }
        ),

        (
            "WhatsApp Numbers",
            {
                "fields": (
                    "whatsapp_number_1",
                    "whatsapp_number_2",
                )
            }
        ),

        (
            "Email Information",
            {
                "fields": (
                    "email_address",
                ),
                "description": "Official administrative email address."
            }
        ),

    )

    def has_add_permission(self, request):
        # Allow only one WebsiteContact object
        if WebsiteContact.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion
        return False
    


@admin.register(WebsiteStat)
class WebsiteStatAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "number",
        "title",
    )

    list_editable = (
        "order",
        "number",
        "title",
    )

    list_display_links = None


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "name",
        "rating",
        "place",
        "show_on_homepage",
    )

    list_editable = (
        "order",
        "rating",
        "show_on_homepage",
    )

    list_display_links = (
        "name",
    )

    search_fields = (
        "name",
        "review",
        "course",
    )