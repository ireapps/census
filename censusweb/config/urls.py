from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
#    url(r'^geo/$', views.generic_view, { "template": "geo-documentation.html" }, name="geo-documentation"),
    (r'^geo/.+', include('boundaryservice.urls')),
    (r'^', include('api.urls')),
)
