from django.conf.urls.defaults import *
from datathing import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    (r'^datathing\.(?P<extension>(json)|(csv))', views.theapi),

    # The Homepage.
    (r'^$', views.homepage)

)
