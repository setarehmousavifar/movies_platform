from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    if isinstance(value, BoundField):
        attrs = value.field.widget.attrs
        existing_classes = attrs.get('class', '')
        attrs['class'] = f"{existing_classes} {css_class}"
        return value
    return value  # اگر ورودی یک فیلد فرم نبود، همان مقدار را بازگرداند.
