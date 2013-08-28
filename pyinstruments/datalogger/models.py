from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class Sensor(models.Model):
    name = models.CharField(max_length = 255)
    
    def __unicode__(self):
        return self.name

class MeasurementPoint(models.Model):
    
    def __unicode__(self):
        return str(self.sensor) + ':'+ str(self.value)
    
    sensor = models.ForeignKey(Sensor,
                               related_name='measurement_points', \
                               blank=True)
    value = models.FloatField()
    time = models.DateTimeField(db_index=True)
    
    @property
    def sensor_name(self):
        return self.sensor.name
    
    @sensor_name.setter
    def sensor_name(self, name):
        try:
            self.sensor = Sensor.objects.get(name=name)
        except ObjectDoesNotExist:
            new_sensor = Sensor(name=name)
            new_sensor.save()
            self.sensor = new_sensor
        return name