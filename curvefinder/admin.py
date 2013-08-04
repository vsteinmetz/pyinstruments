from django.contrib import admin
from curvefinder.models import CurveDB, SpecAnCurve, NaCurve, ScopeCurve

admin.site.register(CurveDB)
admin.site.register(SpecAnCurve)
admin.site.register(NaCurve)
admin.site.register(ScopeCurve)