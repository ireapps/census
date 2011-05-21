from django import template
from django.conf import settings
from urlparse import urljoin
from urllib import quote_plus
import api.help_text
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.simple_tag
def build_media_url(uri):
    """
       Take a bit of url (uri) and put it together with the media url
       urljoin doesn't work like you think it would work. It likes to
       throw bits of the url away unless things are just right.
    """
    uri = "/".join(map(quote_plus,uri.split("/")))
    if getattr(settings,'MEDIA_URL',False):
        if uri.startswith('/'):
            return urljoin(settings.MEDIA_URL,uri[1:])
        else:
            return urljoin(settings.MEDIA_URL,uri)
    else:
        return uri
        
@register.simple_tag
def help_text(key):
    return api.help_text.help_text[key]

@register.filter
def percent(val):
    return val*100
