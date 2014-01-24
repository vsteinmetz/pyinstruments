# Create your views here.
from pyinstruments.curvestore.models import CurveDB

from django.shortcuts import render

def curves(request):
    curves = CurveDB.objects.all()[:5]
    return render(request, "curvestore/curves.html", {'curves':curves})
