from cassandra.cqlengine import columns, models

from utils import tools

class Logs_by_location(models.Model):
    location_id = columns.UUID(primary_key=True)
    log_name = columns.Text(primary_key=True, clustering_order="ASC")
    log_id = columns.UUID()
    log_description = columns.Text(default=None)

    @classmethod
    def get_all_logs(cls, location_id, log_name=None, json_request=None):
        """
        Return all logs belonging to a specific location, or the log with a specific name (if given).
        Return an empty list if not found.

        Keyword arguments:
        location_id -- location identifier (UUID)
        log_name -- name of location (str)
        json_request -- if true, convert uuid to string representation (bool).
        """
        logs_data = []
        all_logs_query = cls.objects.filter(location_id=location_id)
        if log_name:
            all_logs_query = all_logs_query.filter(log_name=log_name)
        for row in all_logs_query:
            if json_request:
                log_id = tools.MiscTools.uuid_to_str(row.log_id)
            else:
                log_id = row.log_id
            log = {
                'log_name' : row.log_name,
                'log_id' : log_id,
                'log_description' : row.log_description
            }
            logs_data.append(log)
        return logs_data

class Log_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    log_name = columns.Text()
    log_description = columns.Text(default=None)

    @classmethod
    def get_log(cls, log_id):
        """
        Return log or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        """
        log_data = []
        log_query = cls.objects.filter(log_id=log_id)
        for row in log_query:
            log = {
                'log_name' : row.log_name,
                'log_description' : row.log_description,
            }
            log_data.append(log)
        return log_data

class Log_file_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    log_file_path = columns.Text(default=None)
    log_file_line_num = columns.Integer(default=1)

    @classmethod
    def get_log_file_info(cls, log_id):
        """
        Return log file info or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        """
        log_file_info_data = []
        log_file_info_query = cls.objects.filter(log_id=log_id)
        for row in log_file_info_query:
            log = {
                'log_file_path' : row.log_file_path,
                'log_file_line_num' : row.log_file_line_num,
            }
            log_file_info_data.append(log)
        return log_file_info_data

class Log_parameters_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    log_parameters = columns.List(columns.Text)
    log_reading_types = columns.Map(columns.Text, columns.Text)

    @classmethod
    def get_log_parameters(cls, log_id):
        """
        Return log parameters or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        """
        log_parameters_data = []
        log_parameters_query = cls.objects.filter(log_id=log_id)
        for row in log_parameters_query:
            log = {
                'log_parameters' : row.log_parameters,
                'log_reading_types' : row.log_reading_types,
            }
            log_parameters_data.append(log)
        return log_parameters_data

class Log_update_schedule_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    log_update_is_active = columns.Boolean(default=False)
    log_last_update = columns.DateTime(default=None)

    @classmethod
    def get_log_updates(cls, log_id):
        """
        Return log update info or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        """
        log_updates_data = []
        log_updates_query = cls.objects.filter(log_id=log_id)
        for row in log_updates_query:
            log = {
                'log_update_is_active' : row.log_update_is_active,
                'log_last_update' : row.log_last_update
            }
            log_updates_data.append(log)
        return log_updates_data

class Log_time_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    log_time_formats = columns.Map(columns.Text, columns.Text)
    log_time_zone = columns.Text()

    @classmethod
    def get_log_time_info(cls, log_id, json_request=None):
        """
        Return log time info or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        json_request -- if true, convert uuid to string representation (bool).
        """
        log_time_info_data = []
        log_time_info_query = cls.objects.filter(log_id=log_id)
        for row in log_time_info_query:
            log = {
                'log_time_formats' : row.log_time_formats,
                'log_time_zone' : row.log_time_zone,
            }
            log_time_info_data.append(log)
        return log_time_info_data

class Logs_by_update(models.Model):
    log_update_is_active = columns.Boolean(primary_key=True, default=False)
    log_id = columns.UUID(primary_key=True, clustering_order="ASC")
    log_last_update = columns.DateTime(default=None)

    @classmethod
    def get_active_logs(cls, log_id=None):
        """Return all logs where automatic updating is active. """
        logs_data = []
        logs_query = cls.objects.filter(log_update_is_active=True)
        if log_id:
            logs_query = logs_query.filter(log_id=log_id)
        for row in logs_query:
            log = {
                'log_id' : row.log_id,
                'log_last_update' : row.log_last_update
            }
            logs_data.append(log)
        return logs_data

    @classmethod
    def get_disabled_logs(cls, log_id=None):
        """Return all logs where automatic updating is disabled. """
        logs_data = []
        logs_query = cls.objects.filter(log_update_is_active=False)
        if log_id:
            logs_query = logs_query.filter(log_id=log_id)
        for row in logs_query:
            log = {
                'log_id' : row.log_id,
                'log_last_update' : row.log_last_update
            }
            logs_data.append(log)
        return logs_data