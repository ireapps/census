from django.conf.urls.defaults import *
from api import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # The Homepage.
    (r'^$', views.homepage),

    # Tracts
    #/tracts/IL.json
    #/tracts/IL/123.json
    #/tracts/IL/123/12345.json
    (r'tracts/(?P<state>[A-Z]{2})(/(?P<county>\d{3}))?(/(?P<tract>\d{6}))?\.(?P<extension>json|csv|html)$', views.tracts)
)
