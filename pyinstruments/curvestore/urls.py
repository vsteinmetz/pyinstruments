from django.conf.urls import patterns, url
from pyinstruments.curvestore import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sam_site.views.home', name='home'),
    # url(r'^sam_site/', include('sam_site.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^curves', views.curves, name="curves"),
)