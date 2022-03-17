from django import template

from ..utils import get_tenant_model

register = template.Library()


@register.filter
def is_tenant_model(obj):
    return isinstance(obj, get_tenant_model())
