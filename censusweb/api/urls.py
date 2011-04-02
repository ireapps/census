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
    (r'^tracts/(?P<state>[A-Z]{2})(/(?P<county>\d{3}))?(/(?P<tract>\d{6}))?\.(?P<extension>json|csv|html)$', views.tracts),

    # County codes for states.
    #/internal/counties_for_state/CA.json
    (r'^internal/counties_for_state/(?P<state>[A-Z]{2}).json$', views.counties_for_state),

    # Place names for states.
    #/internal/places_for_state/IL.json
    (r'^internal/places_for_state/(?P<state>[A-Z]{2}).json$', views.places_for_state),

    # Subdivisions for a given county.
    #/internal/subdivisions_for_county/IL.json
    (r'^internal/subdivisions_for_county/(?P<county>TBD).json$', views.subdivisions_for_county),

    (r'stats/(?P<group>[-A-Za-z]+)/?$', views.stats),
)
