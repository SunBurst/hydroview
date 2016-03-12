from .models import Logger_time_formats, Logger_time_format_by_logger_time_format, Log_time_info_by_log, \
    Logs_by_logger_time_format
from utils.tools import MiscTools

class LoggerData(object):
    """Helper class for getting logger related data from the Cassandra database. """

    @classmethod
    def get_all_logger_time_formats(cls, json_request=None):
        """Return all logger time formats or an empty list if not found.

        Keyword arguments:
        json_request -- if true, convert uuid to string representation (bool).
        """
        logger_time_formats_data = []
        all_time_formats_query = Logger_time_formats.objects.filter(bucket=0)
        for row in all_time_formats_query:
            if json_request:
                logger_time_format_id = MiscTools.uuid_to_str(row.logger_time_format_id)
            else:
                logger_time_format_id = row.logger_time_format_id
            time_format = {
                'logger_time_format_id' : logger_time_format_id,
                'logger_time_format_name' : row.logger_time_format_name,
                'logger_time_format_description' : row.logger_time_format_description,
            }
            logger_time_formats_data.append(time_format)
        return logger_time_formats_data

    @classmethod
    def get_logger_time_format(cls, logger_time_format_id):
        """
        Return logger time format or an empty list if not found.

        Keyword arguments:
        logger_time_format_id -- logger time format (UUID)
        """
        logger_time_formats_data = []
        time_format_query = Logger_time_format_by_logger_time_format.objects.filter(
            logger_time_format_id=logger_time_format_id
        )
        for row in time_format_query:
            time_format = {
                'logger_time_format_name' : row.logger_time_format_name,
                'logger_time_format_description' : row.logger_time_format_description,
                'logger_time_ids' : row.logger_time_ids,
                'logger_time_id_types' : row.logger_time_id_types
            }
            logger_time_formats_data.append(time_format)
        return logger_time_formats_data

    @classmethod
    def get_logs_by_logger_time_format(cls, logger_time_format_id):
        """
        Return logs using the given logger time format or an empty list if not found.

        Keyword arguments:
        logger_time_format_id -- logger time format (UUID)
        """
        logs_data = []
        all_logs_query = Logs_by_logger_time_format.objects.filter(logger_time_format_id=logger_time_format_id)
        for row in all_logs_query:
            log = {
                'log_id' : row.log_id
            }
            logs_data.append(log)
        return logs_data

    @classmethod
    def get_log_time_info(cls, log_id):
        """
        Return log time info or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        """
        log_time_info_data = []
        log_time_info_data_query = Log_time_info_by_log.objects.filter(log_id=log_id)
        for row in log_time_info_data_query:
            log = {
                'logger_time_format_id' : row.logger_time_format_id,
                'logger_time_format_name' : row.logger_time_format_name,
                'log_time_ids' : row.log_time_ids,
                'log_time_zone' : row.log_time_zone
            }
            log_time_info_data.append(log)
        return log_time_info_data
