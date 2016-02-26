from cassandra.cqlengine import columns
from cassandra.cqlengine import models

# Create your models here.

class Sites(models.Model):
    bucket = columns.Integer(primary_key=True, default=0)
    site_id = columns.UUID(primary_key=True)
    site_name = columns.Text(primary_key=True, clustering_order="ASC")
    description = columns.Text(default=None)
    position = columns.Map(columns.Text, columns.Float, default=None)

class Site_info_by_site(models.Model):
    site_id = columns.UUID(primary_key=True)
    site_name = columns.Text()
    description = columns.Text(default=None)
    position = columns.Map(columns.Text, columns.Float, default=None)

class Locations_by_site(models.Model):
    site_id = columns.UUID(primary_key=True)
    location_name = columns.Text(primary_key=True, clustering_order="ASC")
    location_id = columns.UUID()
    description = columns.Text(default=None)
    position = columns.Map(columns.Text, columns.Float, default=None)

class Location_info_by_location(models.Model):
    location_id = columns.UUID(primary_key=True)
    location_name = columns.Text
    description = columns.Text()
    position = columns.Map(columns.Text, columns.Float)

class Logs_by_location(models.Model):
    location = columns.UUID(primary_key=True)
    log_name = columns.Text(primary_key=True, clustering_order="ASC")
    log_id = columns.UUID()
    description = columns.Text()

class Log_file_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    file_path = columns.Text()
    file_line_num = columns.Integer(default=0)

class Log_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    log_name = columns.Text()
    description = columns.Text()

class Log_parameters_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    parameters = columns.List(columns.Text)
    reading_types = columns.Map(columns.Text, columns.Text) #: I.e. ignore, time, parameter, profile, status

class Log_update_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    last_update = columns.DateTime()
    next_update = columns.DateTime()

class Parameters_readings_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    qc_level = columns.Integer(primary_key=True, partition_key=True)
    parameter = columns.Text(primary_key=True, partition_key=True)
    time = columns.DateTime(primary_key=True, clustering_order="DESC")
    value = columns.Float()

class Profiles_readings_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    qc_level = columns.Integer(primary_key=True, partition_key=True)
    profile = columns.Text(primary_key=True, partition_key=True)
    time = columns.DateTime(primary_key=True, clustering_order="DESC")
    profile_values = columns.Map(columns.Text, columns.Float)

class Status_parameter_readings_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    qc_level = columns.Integer(primary_key=True, partition_key=True)
    parameter = columns.Text(primary_key=True, partition_key=True)
    time = columns.DateTime(primary_key=True, clustering_order="DESC")
    value = columns.Float()

class Quality_controls(models.Model):
    bucket = columns.Integer(primary_key=True, default=0)
    qc_level = columns.Integer(primary_key=True, clustering_order="ASC")
    qc_name = columns.Text()
    qc_description = columns.Text()

class Quality_control_info_by_quality_control(models.Model):
    qc_level = columns.Integer(primary_key=True)
    qc_name = columns.Text()
    qc_description = columns.Text()
    qc_replacement_value = columns.Float()

class Quality_control_level_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    qc_level = columns.Integer(primary_key=True, clustering_order="ASC")
    qc_name = columns.Text()
    qc_replacement_value = columns.Float()

class Quality_control_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    qc_level = columns.Integer(primary_key=True, partition_key=True)
    month_first_day = columns.DateTime(primary_key=True, clustering_order="DESC", default=0) #: Set to epoch for level 1
    qc_parameters = columns.List(columns.Text)  # Used for all levels. Indicates which parameters to check
    qc_minute_interval = columns.Integer()  # Used for level 1
    qc_parameters_min_values = columns.Map(columns.Text, columns.Float) # Used for level 2, 4
    qc_parameters_max_values = columns.Map(columns.Text, columns.Float) # Used for level 2, 4
    qc_window = columns.Map(columns.Text, columns.Integer) # Used for level 3, 4
    qc_replacement_value = columns.Float() # static

class Log_quality_control_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    qc_level = columns.Integer(primary_key=True, clustering_order="ASC")
    last_quality_control = columns.DateTime()
    next_quality_control = columns.DateTime()

class Logger_types(models.Model):
    bucket = columns.Integer(primary_key=True, default=0)
    type_name = columns.Text(primary_key=True, clustering_order="ASC")
    type_description = columns.Text()

class Logger_type_by_logger_type(models.Model):
    type_name = columns.Text(primary_key=True)
    type_description = columns.Text()
    time_formats = columns.Map(columns.Text, columns.Text)

class Logger_time_format_by_logger_type(models.Model):
    type_name = columns.Text(primary_key=True, partition_key=True)
    time_format = columns.Text(primary_key=True, partition_key=True)
    time_ids = columns.Map(columns.Text, columns.Text)

class Log_time_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    type_name = columns.Text()
    time_format = columns.Text()
    time_ids = columns.Map(columns.Text, columns.Text)
    time_zone = columns.Text()