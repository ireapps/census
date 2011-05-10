from django.conf.urls.defaults import *
from api import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # The Homepage.
    (r'^$', views.homepage),

    # Data
    #/data/tract-AL-003-010100.html
    #/data/state-AL.html
    #/data/tract-AL-003-010100/tract-AL-003-010120/state-AL.html
    (r'^data/(?P<slugs>(/?tract-[A-Z]{2}(-\d{3})?(-\d{6})?)+)\.(?P<extension>json|csv|html)$', views.data),

    # Tracts
    #/tracts/IL.json
    #/tracts/IL/123.json
    #/tracts/IL/123/12345.json
    # (r'^tracts/(?P<state>[A-Z]{2})(/(?P<county>\d{3}))?(/(?P<tract>\d{6}))?\.(?P<extension>json|csv|html)$', views.tracts),

    # County codes for states.
    #/internal/counties_for_state/CA.json
    (r'^internal/counties_for_state/(?P<state>[A-Z]{2}).json$', views.counties_for_state),

    # Place names for states.
    #/internal/places_for_state/IL.json
    (r'^internal/places_for_state/(?P<state>[A-Z]{2}).json$', views.places_for_state),

    # Tracts for a given county.
    #/internal/tracts_for_county/10101.json
    (r'^internal/tracts_for_county/(?P<county>\d{5}).json$', views.tracts_for_county),

    (r'stats/(?P<group>[-A-Za-z]+)/?$', views.stats),
)
