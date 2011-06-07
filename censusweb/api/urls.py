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
    url(r'^data/(?P<geoids>[,\d]+)\.json$', views.data_as_json, name="data_as_json"),
    url(r'^data/(?P<geoids>[,\d]+)\.csv$', views.data_as_csv, name="data_as_csv"),
    url(r'^data/(?P<geoids>[,\d]+)\.(?P<format>kml|kmz)$', views.data_as_kml, name="data_as_kml"),
    url(r'^data/(?P<geoids>[,\d]+)\.html$', views.data, name="data"),

    # Generate CSV/JSON for all elements in a given region (used from within Query Builder)
    #/internal/download_data_for_region/10.csv (or .json)
    (r'^internal/download_data_for_region/(?P<sumlev>\d{3})-(?P<containerlev>\d{3})-(?P<container>\d+)\.(?P<datatype>csv|json)$', views.download_data_for_region),
)
