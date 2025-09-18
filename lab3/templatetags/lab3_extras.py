from django import template

register = template.Library()


@register.filter
def get_item(dictionary_or_list, key):
    try:
        return dictionary_or_list[key]
    except (IndexError, KeyError, TypeError):
        return None
