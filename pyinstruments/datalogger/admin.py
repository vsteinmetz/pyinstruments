from django.contrib import admin
from pyinstruments.datalogger.models import MeasurementPoint, Sensor

admin.site.register(MeasurementPoint)
admin.site.register(Sensor)
