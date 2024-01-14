from urllib.parse import urlparse
from django import template

register = template.Library()

@register.filter(name='url_parse')
def url_parse(value):
    # Convert ImageFieldFile to string
    value_str = str(value)

    # Split the path by '/'
    path_list = value_str.split('/')

    # Check if 'media' is in the path list
    if 'media' in path_list:
        return value_str
    else:
        return f'media/{value_str}'
