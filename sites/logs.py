from .models import Logs_by_location, Log_info_by_log, Log_file_info_by_log, Log_parameters_by_log,\
    Log_update_info_by_log

class LogData(object):
    """Helper class for getting log related data from the Cassandra database. """

    @classmethod
    def get_all_logs(cls, location_id):
        """
        Return all logs belonging to a specific location or an empty list if not found.

        Keyword arguments:
        location_id -- location identifier (UUID)
        """
        logs_data = []
        all_logs_query = Logs_by_location.objects.filter(location_id=location_id)
        for row in all_logs_query:
            log = {
                'log_name' : row.log_name,
                'log_id' : row.log_id,
                'description' : row.description
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
                'description' : row.description,
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
                'file_path' : row.file_path,
                'file_line_num' : row.file_line_num,
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
                'parameters' : row.parameters,
                'reading_types' : row.reading_types,
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
        log_updates_query = Log_update_info_by_log.objects.filter(log_id=log_id)
        for row in log_updates_query:
            log = {
                'last_update' : row.last_update,
                'next_update' : row.next_update,
            }
            log_updates_data.append(log)
        return log_updates_data