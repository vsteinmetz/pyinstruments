from django.contrib import admin
from curvefinder.models import Curve, SpecAnCurve, NaCurve, ScopeCurve

admin.site.register(Curve)
admin.site.register(SpecAnCurve)
admin.site.register(NaCurve)
admin.site.register(ScopeCurve)