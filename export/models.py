#from django.db import models

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

# Create your models here.

class Locations(Model):
    bucket = columns.Integer(primary_key=True, default=0)
    name = columns.Text(primary_key=True, clustering_order="ASC")
    description = columns.Text()
    latitude = columns.Float()
    longitude = columns.Float()

class Sensors(Model):
    bucket = columns.Integer(primary_key=True, default=0) 
    name = columns.Text(primary_key=True, clustering_order="ASC")
    description = columns.Text()
    num_sensors = columns.Integer()
    latitude = columns.Float()
    longitude = columns.Float()

class Sensors_by_location(Model):
    location = columns.Text(primary_key=True) 
    sensor = columns.Text(primary_key=True, clustering_order="ASC") 

class Readings_by_sensor(Model):
    sensor = columns.Text(primary_key=True, partition_key=True)
    parameter = columns.Text(primary_key=True, partition_key=True)
    time = columns.DateTime(primary_key=True, clustering_order="DESC") 
    value = columns.Float()

class Sensor_status_by_location(Model):
    location = columns.Text(primary_key=True)
    last_connected = columns.DateTime()
    battery_status = columns.Text()