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
    #/data/10,10001,10001041500.html
    (r'^data/(?P<geoids>[,\d]+)\.json$', views.data_as_json),
    (r'^data/(?P<geoids>[,\d]+)\.csv$', views.data_as_csv),
    url(r'^data/(?P<geoids>[,\d]+)\.html$', views.data, name="data"),

    (r'^family/(?P<geoid>\d+)/$', views.redirect_to_family),
    (r'^family/(?P<geoid>\d+)\.json$', views.family_as_json),

    (r'^labels/(?P<year>\d{4})(/(?P<tables>.+))?.json', views.labels_as_json),

    # County codes for states.
    #/internal/counties_for_state/10.json
    (r'^internal/counties_for_state/(?P<state>\d{2}).json$', views.counties_for_state),

    # Place names for states.
    #/internal/places_for_state/10.json
    (r'^internal/places_for_state/(?P<state>\d{2}).json$', views.places_for_state),

    # Tracts for a given county.
    #/internal/tracts_for_county/10101.json
    (r'^internal/tracts_for_county/(?P<county>\d{5}).json$', views.tracts_for_county),

    # Tracts for a given state.
    #/internal/tracts_for_state/10.json
    (r'^internal/tracts_for_state/(?P<state>\d{2}).json$', views.tracts_for_state),
    
    # Generate CSV/JSON for all elements in a given region (used from within Query Builder)
    #/internal/download_data_for_region/10.csv (or .json)
    (r'^internal/download_data_for_region/(?P<sumlev>\d{3})-(?P<containerlev>\d{3})-(?P<container>\d+)\.(?P<datatype>csv|json)$', views.download_data_for_region),
)
