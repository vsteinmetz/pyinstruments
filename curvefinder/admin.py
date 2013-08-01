from django.contrib import admin
from curvefinder.models import Curve, Tag, InstrumentType, \
                                        InstrumentLogicalName

admin.site.register(Curve)
admin.site.register(Tag)
admin.site.register(InstrumentType)
admin.site.register(InstrumentLogicalName)