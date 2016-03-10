from cassandra.cqlengine import columns
from cassandra.cqlengine import models

# Create your models here.

class Sites(models.Model):
    bucket = columns.Integer(primary_key=True, default=0)
    site_id = columns.UUID(primary_key=True)
    site_name = columns.Text(primary_key=True, clustering_order="ASC")
    site_description = columns.Text(default=None)
    site_position = columns.Map(columns.Text, columns.Float, default=None)

class Site_info_by_site(models.Model):
    site_id = columns.UUID(primary_key=True)
    site_name = columns.Text()
    site_description = columns.Text(default=None)
    site_position = columns.Map(columns.Text, columns.Float, default=None)

class Locations_by_site(models.Model):
    site_id = columns.UUID(primary_key=True)
    location_name = columns.Text(primary_key=True, clustering_order="ASC")
    location_id = columns.UUID()
    location_description = columns.Text(default=None)
    location_position = columns.Map(columns.Text, columns.Float, default=None)

class Location_info_by_location(models.Model):
    location_id = columns.UUID(primary_key=True)
    location_name = columns.Text()
    location_description = columns.Text(default=None)
    location_position = columns.Map(columns.Text, columns.Float, default=None)

class Logs_by_location(models.Model):
    location_id = columns.UUID(primary_key=True)
    log_name = columns.Text(primary_key=True, clustering_order="ASC")
    log_id = columns.UUID()
    log_description = columns.Text(default=None)

class Log_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    log_name = columns.Text()
    log_description = columns.Text(default=None)

class Log_file_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    log_file_path = columns.Text(default=None)
    log_file_line_num = columns.Integer(default=0)

class Log_parameters_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    log_parameters = columns.List(columns.Text)
    log_reading_types = columns.Map(columns.Text, columns.Text) #: I.e. ignore, time, parameter, profile, status

class Log_update_schedule_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    log_last_update = columns.DateTime(default=None)
    log_next_update = columns.DateTime(default=None)

class Parameters_readings_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    reading_qc_level = columns.Integer(primary_key=True, partition_key=True)
    reading_parameter = columns.Text(primary_key=True, partition_key=True)
    reading_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    reading_value = columns.Float()

class Profiles_readings_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    reading_qc_level = columns.Integer(primary_key=True, partition_key=True)
    reading_profile = columns.Text(primary_key=True, partition_key=True)
    reading_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    reading_values = columns.Map(columns.Text, columns.Float)

class Status_parameter_readings_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    reading_qc_level = columns.Integer(primary_key=True, partition_key=True)
    reading_parameter = columns.Text(primary_key=True, partition_key=True)
    reading_time = columns.DateTime(primary_key=True, clustering_order="DESC")
    reading_value = columns.Float()

class Quality_controls(models.Model):
    bucket = columns.Integer(primary_key=True, default=0)
    qc_level = columns.Integer(primary_key=True, clustering_order="ASC")
    qc_name = columns.Text()
    qc_description = columns.Text()

class Quality_control_info_by_quality_control(models.Model):
    qc_level = columns.Integer(primary_key=True)
    qc_name = columns.Text()
    qc_description = columns.Text()

class Quality_control_level_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    qc_level = columns.Integer(primary_key=True, clustering_order="ASC")
    qc_name = columns.Text()
    qc_replacement_value = columns.Float()

class Quality_control_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    qc_level = columns.Integer(primary_key=True, partition_key=True)
    month_first_day = columns.DateTime(primary_key=True, clustering_order="DESC", default=0) #: Set to epoch for level 1
    qc_parameters = columns.List(columns.Text)  # Used for all levels. Indicates which parameters to check
    qc_time_interval = columns.Integer()  # Used for level 1
    qc_parameters_min_values = columns.Map(columns.Text, columns.Float) # Used for level 2, 4
    qc_parameters_max_values = columns.Map(columns.Text, columns.Float) # Used for level 2, 4
    qc_window_sizes = columns.Map(columns.Text, columns.Integer) # Used for level 3, 4
    qc_replacement_value = columns.Float() # static

class Log_quality_control_schedule_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    qc_level = columns.Integer(primary_key=True, clustering_order="ASC")
    log_last_quality_control = columns.DateTime()
    log_next_quality_control = columns.DateTime()

class Logger_time_formats(models.Model):
    bucket = columns.Integer(primary_key=True, default=0)
    logger_time_format_id = columns.UUID(primary_key=True)
    logger_time_format_name = columns.Text(primary_key=True, clustering_order="ASC")
    logger_time_format_description = columns.Text(default=None)

class Logger_time_format_by_logger_time_format(models.Model):
    logger_time_format_id =  columns.UUID(primary_key=True)
    logger_time_format_name = columns.Text()
    logger_time_format_description = columns.Text(default=None)
    logger_time_ids = columns.List(columns.Text)
    logger_time_id_types = columns.Map(columns.Text, columns.Text)

class Logs_by_logger_time_format(models.Model):
    logger_time_format_id = columns.UUID(primary_key=True)
    log_id = columns.UUID(primary_key=True, clustering_order="ASC")

class Log_time_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    logger_time_format_id = columns.UUID()
    logger_time_format_name = columns.Text()
    log_time_ids = columns.List(columns.Text)
    log_time_zone = columns.Text()