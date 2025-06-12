from django import template
import os

register = template.Library()

@register.filter
def basename(value):
    """Return the base name of a file path."""
    return os.path.basename(value)
