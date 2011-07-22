from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to
from django.core.urlresolvers import reverse

urlpatterns = patterns('',
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
    (r'^geo/$', redirect_to, { 'url': "/docs/boundary.html"}),
#    (r'^geo/$', redirect_to, { 'url': reverse("boundary-documentation")}),
    (r'^geo/', include('boundaryservice.urls')),
    (r'^', include('api.urls')),
)
