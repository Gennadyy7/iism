from django import template

register = template.Library()


@register.filter
def get_field_by_name(form, field_name):
    return form[field_name]
