from django.contrib import admin
from curvefinder.models import Curve

class TagInline(admin.TabularInline):
   model = Tag

class CurveAdmin(admin.ModelAdmin):
   inlines = [
       TagInline
   ]
admin.site.register(Curve, CurveAdmin)