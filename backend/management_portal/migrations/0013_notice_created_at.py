from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ("management_portal", "0012_alter_notice_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="notice",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=timezone.now
            ),
            preserve_default=False,
        ),
    ]