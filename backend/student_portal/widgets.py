from django.forms.widgets import ClearableFileInput
from django.utils.html import format_html


class PreviewFileWidget(ClearableFileInput):

    def render(self, name, value, attrs=None, renderer=None):
        # Get default Django layout
        html = super().render(name, value, attrs, renderer)

        # Add eye icon only if file exists
        if value and hasattr(value, "url"):
            html += format_html(
                ' <a href="{}" target="_blank" style="margin-left:8px;">👁</a>',
                value.url
            )

        return html
