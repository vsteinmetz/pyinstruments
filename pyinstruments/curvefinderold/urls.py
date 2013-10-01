from django.conf.urls import patterns, url
from .views import CurveListView, CurveDetailView


urlpatterns = patterns('',
                       url(r'^$', CurveListView.as_view(), name='curves_list'),
                       url(r'^(?P<pk>\d+)/$', \
            CurveDetailView.as_view(), name="curves_detail"),
                       )
