from cassandra.cqlengine import columns
from cassandra.cqlengine import models

# Create your models here.

class Sites(models.Model):
    bucket = columns.Integer(primary_key=True, default=0)
    site = columns.Text(primary_key=True, clustering_order="ASC")
    description = columns.Text()
    latitude = columns.Float()
    longitude = columns.Float()

class Site_info_by_site(models.Model):
    site = columns.Text(primary_key=True)
    description = columns.Text()
    latitude = columns.Float()
    longitude = columns.Float()

class Locations_by_site(models.Model):
    site = columns.Text(primary_key=True)
    location = columns.Text(primary_key=True, clustering_order="ASC")
    description = columns.Text()
    latitude = columns.Float()
    longitude = columns.Float()

class Location_info_by_location(models.Model):
    location = columns.Text(primary_key=True)
    description = columns.Text()
    latitude = columns.Float()
    longitude = columns.Float()

class Sensors_by_location(models.Model):
    location = columns.Text(primary_key=True)
    sensor = columns.Text(primary_key=True, clustering_order="ASC")
    sensor_num = columns.Integer()
    description = columns.Text()

class Sensor_info_by_sensor(models.Model):
    sensor = columns.Text(primary_key=True)
    description = columns.Text()
    parameters = columns.List(columns.Text)
    file_path = columns.Text()
    file_line_num = columns.Integer()
    time_zone = columns.Text()
    time_ids = columns.List(columns.Text)

class Parameters_by_sensor(models.Model):
    sensor = columns.Text(primary_key=True, partition_key=True)
    qc_level = columns.Integer(primary_key=True, partition_key=True)
    parameter = columns.Text(primary_key=True, partition_key=True)
    time = columns.DateTime(primary_key=True, clustering_order="DESC")
    value = columns.Float()

class Profiles_by_sensor(models.Model):
    sensor = columns.Text(primary_key=True, partition_key=True)
    qc_level = columns.Integer(primary_key=True, partition_key=True)
    time = columns.DateTime(primary_key=True, clustering_order="DESC")
    profile = columns.Map(columns.Text, columns.Float)

class Qc_info_by_sensor(models.Model):
    sensor = columns.Text(primary_key=True)
    qc_level = columns.Integer(primary_key=True, clustering_order="ASC")
    name = columns.Text()
    parameters = columns.List(columns.Text)
    replacement_value = columns.Float()

class Qc_level_1_by_sensor(models.Model):
    sensor = columns.Text(primary_key=True)
    time_interval = columns.Integer()

class Qc_level_2_by_sensor(models.Model):
    sensor = columns.Text(primary_key=True, partition_key=True)
    month_first_day = columns.DateTime(primary_key=True, partition_key=True)
    min_values = columns.Map(columns.Text, columns.Float)
    max_values = columns.Map(columns.Text, columns.Float)

class Qc_level_3_by_sensor(models.Model):
    sensor = columns.Text(primary_key=True)
    window_size = columns.Map(columns.Text, columns.Integer)