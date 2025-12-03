from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag(takes_context=True)
def get_fullpath(context, path):
    request = context.get("request")
    url = static(path)
    return request.build_absolute_uri(url) if request else url
