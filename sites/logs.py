from .models import Logs_by_location, Log_info_by_log, Log_file_info_by_log, Log_parameters_by_log,\
    Log_update_schedule_by_log

class LogData(object):
    """Helper class for getting log related data from the Cassandra database. """

    @classmethod
    def get_all_logs(cls, location_id, log_name=None):
        """
        Return all logs belonging to a specific location, or the log with a specific name (if given).
        Return an empty list if not found.

        Keyword arguments:
        location_id -- location identifier (UUID)
        log_name -- name of location (str)
        """
        logs_data = []
        all_logs_query = Logs_by_location.objects.filter(location_id=location_id)
        if log_name:
            all_logs_query.filter(log_name=log_name)
        for row in all_logs_query:
            log = {
                'log_name' : row.log_name,
                'log_id' : row.log_id,
                'log_description' : row.log_description
            }
            logs_data.append(log)
        return logs_data

    @classmethod
    def get_log(cls, log_id):
        """
        Return log or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        """
        log_data = []
        log_query = Log_info_by_log.objects.filter(log_id=log_id)
        for row in log_query:
            log = {
                'log_name' : row.log_name,
                'log_description' : row.log_description,
            }
            log_data.append(log)
        return log_data

    @classmethod
    def get_log_file_info(cls, log_id):
        """
        Return log file info or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        """
        log_file_info_data = []
        log_file_info_query = Log_file_info_by_log.objects.filter(log_id=log_id)
        for row in log_file_info_query:
            log = {
                'log_file_path' : row.log_file_path,
                'log_file_line_num' : row.log_file_line_num,
            }
            log_file_info_data.append(log)
        return log_file_info_data

    @classmethod
    def get_log_parameters(cls, log_id):
        """
        Return log parameters or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        """
        log_parameters_data = []
        log_parameters_query = Log_parameters_by_log.objects.filter(log_id=log_id)
        for row in log_parameters_query:
            log = {
                'log_parameters' : row.log_parameters,
                'log_reading_types' : row.log_reading_types,
            }
            log_parameters_data.append(log)
        return log_parameters_data

    @classmethod
    def get_log_updates(cls, log_id):
        """
        Return log update info or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        """
        log_updates_data = []
        log_updates_query = Log_update_schedule_by_log.objects.filter(log_id=log_id)
        for row in log_updates_query:
            log = {
                'log_last_update' : row.log_last_update,
                'log_next_update' : row.log_next_update,
            }
            log_updates_data.append(log)
        return log_updates_data