from django.template import Library

register = Library()


@register.filter
def absolute_media_uri(path, request):
    """Build an absolute URI for media/CDN poster paths."""
    if not path:
        return ''
    if str(path).startswith(('http://', 'https://')):
        return str(path)
    return request.build_absolute_uri(path)
