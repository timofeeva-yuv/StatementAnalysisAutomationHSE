from django import template
from ..models import MenuItem


register = template.Library()


@register.simple_tag
def get_menu_items():
    return MenuItem.objects.order_by('order')
