import os

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@register.simple_tag(takes_context=True)
def get_fullpath(context, path):
    request = context.get("request")
    url = static(path)
    return request.build_absolute_uri(url) if request else url


@register.simple_tag
def static_version(path):
    url = static(path)
    full_path = finders.find(path)
    if not full_path:
        return url
    try:
        version = int(os.path.getmtime(full_path))
    except OSError:
        return url
    joiner = "&" if "?" in url else "?"
    return f"{url}{joiner}v={version}"
