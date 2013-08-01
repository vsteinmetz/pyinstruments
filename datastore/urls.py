from django.conf.urls import patterns, include, url
import curvefinder.urls
from curvefinder.views import CurveMergeView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'datastore.views.home', name='home'),
    # url(r'^datastore/', include('datastore.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^curves/', include(curvefinder.urls)),
    url(r'^merge/$', \
        CurveMergeView.as_view(), name="curves_merge")
)
