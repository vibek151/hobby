from django import template

register = template.Library()

@register.filter
def get_item(data, key):
    try:
        return data.get(key)
    except Exception:
        return None