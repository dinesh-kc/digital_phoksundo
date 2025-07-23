# darta_chalani/templatetags/darta_filters.py
from django import template
import os
import nepali_datetime # Import nepali_datetime
from datetime import date as dt_date # Alias datetime.date

register = template.Library()

@register.filter
def filename(value):
    """
    Returns the basename of a file path (just the filename without the directory).
    For example: "uploads/documents/my_file.pdf" -> "my_file.pdf"
    """
    if value:
        return os.path.basename(value.name) # Use .name for FileField, which gives the path string
    return ''

@register.filter
def split_path_last(value, separator='/'):
    """
    Splits a string by the given separator and returns the last element.
    Useful for getting just the filename from a path.
    """
    if isinstance(value, str):
        return value.split(separator)[-1]
    # If it's a FileField or ImageField, its .name attribute is the path string
    elif hasattr(value, 'name') and isinstance(value.name, str):
        return value.name.split(separator)[-1]
    return value

@register.filter
def to_nepali_date(value):
    """Convert a datetime.date (AD) to Nepali BS date string."""
    if value:
        try:
            np_date = nepali_datetime.date.from_datetime_date(value)
            return np_date.strftime('%Y-%m-%d')  # Format like 2081-04-08
        except Exception:
            return value  # Fallback if error
    return ""
# # darta_chalani/templatetags/darta_filters.py
# from django import template
# import os

# register = template.Library()

# @register.filter
# def filename(value):
#     """
#     Returns the basename of a file path (just the filename without the directory).
#     For example: "uploads/documents/my_file.pdf" -> "my_file.pdf"
#     """
#     if value:
#         return os.path.basename(value.name) # Use .name for FileField, which gives the path string
#     return ''

# @register.filter
# def split_path_last(value, separator='/'):
#     """
#     Splits a string by the given separator and returns the last element.
#     Useful for getting just the filename from a path.
#     """
#     if isinstance(value, str):
#         return value.split(separator)[-1]
#     # If it's a FileField or ImageField, its .name attribute is the path string
#     elif hasattr(value, 'name') and isinstance(value.name, str):
#         return value.name.split(separator)[-1]
#     return value