from django.conf.urls.defaults import *
from api import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # The Homepage.
    (r'^$', views.homepage),

    # Data
    #/data/10.html
    #/data/10001.html
    #/data/10001041500.html
    #/data/10/10001/10001041500.html
    (r'^data/(?P<geoids>(/?\d+)+)\.(?P<extension>json|csv|html)$', views.data),

    # County codes for states.
    #/internal/counties_for_state/10.json
    (r'^internal/counties_for_state/(?P<state>\d{2}).json$', views.counties_for_state),

    # Place names for states.
    #/internal/places_for_state/10.json
    (r'^internal/places_for_state/(?P<state>\d{2}).json$', views.places_for_state),

    # Tracts for a given county.
    #/internal/tracts_for_county/10101.json
    (r'^internal/tracts_for_county/(?P<county>\d{5}).json$', views.tracts_for_county),
)
