from itertools import izip
from numpy import sin
import random
import json
import os

from pandas import HDFStore
from django.conf import settings
from django.views.generic import ListView, DetailView, TemplateView
from pyinstruements.curvefinder.models import Curve


class CurveListView(ListView):
    """
    Generic view class for displaying all website
    projects owned by the user
    """
    
    model = Curve


class CurveDetailView(DetailView):

    model = Curve

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CurveDetailView, self).get_context_data(**kwargs)

        store = HDFStore(os.path.join(settings.MEDIA_ROOT, context['object'].data_file.name))
        s = store['data']
        curve_plot = [[i, v] for i, v in izip(s.index, s.values)]
        """
        curve_plot = []
        for i in range(0, 20000):
            curve_plot.append([i, sin(1.9* i/10000) + 0.1 * random.random()])
        """
        context["curve_plot"] = json.dumps(curve_plot)
        return context
    
class CurveMergeView(TemplateView):
    
    model = Curve
    template_name = "curve.html"#"C:/Users/Samuel/Documents/GitHub/pyinstruments-datastore/datastore/curvefinder/templates/curvefinder/curve.html"
    
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CurveMergeView, self).get_context_data(**kwargs)

        context["coucou"] = "coucou"
        return context