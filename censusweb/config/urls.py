from django.conf.urls.defaults import *
from datathing import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    (r'^datathing\.(?P<extension>(json)|(csv))', views.theapi),

    # The Homepage.
    (r'^$', views.homepage)

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    
    #(r'^datathing\.(?P<extension>(json)|(csv))', views.theapi)
    #/tracts/illinois.json
    #/tracts/illinois/cook.json
    #/tracts/illinois/cook/00001.json
    
    #/places/illinois.json
    #/counties/illinois.json
    #/states/illinois.json
    #/states.json
    
    #/illinois/tracts.json
    
    (r'tracts/(?P<state>[A-Z]{2})(/(?P<county>\d{3}))?(/(?P<tract>\d{5}))?\.(?P<extension>json|csv|html)', views.tracts)
)
