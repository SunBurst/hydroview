from .models import Logger_types, Logger_type_by_logger_type, Logger_time_format_by_logger_type, Log_time_info_by_log

class LoggerData(object):
    """Helper class for getting logger related data from the Cassandra database. """

    @classmethod
    def get_all_loggers(cls):
        """Return all quality controls or an empty list if not found. """
        loggers_data = []
        all_loggers_query = Logger_types.objects.filter(bucket=0)
        for row in all_loggers_query:
            logger = {
                'logger_type_name' : row.logger_type_name,
                'logger_type_description' : row.logger_type_description,
            }
            loggers_data.append(logger)
        return loggers_data

    @classmethod
    def get_logger(cls, logger_type_name):
        """
        Return logger type or an empty list if not found.

        Keyword arguments:
        logger_type_name -- logger type identifier (str)
        """
        logger_data = []
        logger_query = Logger_type_by_logger_type.objects.filter(logger_type_name=logger_type_name)
        for row in logger_query:
            logger = {
                'logger_type_description' : row.logger_type_description,
                'logger_time_formats' : row.logger_time_formats,
            }
            logger_data.append(logger)
        return logger_data

    @classmethod
    def get_logger_time_ids(cls, logger_type_name, logger_time_format):
        """
        Return logger type time identifiers for a specific time format, or return an empty list if not found.

        Keyword arguments:
        logger_type_name -- logger type identifier (str)
        logger_time_format -- logger type time format identifier (str)
        """
        logger_data = []
        logger_query = Logger_time_format_by_logger_type.objects.filter(logger_type_name=logger_type_name, logger_time_format=logger_time_format)
        for row in logger_query:
            logger = {
                'logger_time_ids' : row.logger_time_ids
            }
            logger_data.append(logger)
        return logger_data

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
                'logger_type_name' : row.logger_type_name,
                'logger_time_format' : row.logger_time_format,
                'logger_time_ids' : row.logger_time_ids,
                'log_time_zone' : row.log_time_zone
            }
            log_time_info_data.append(log)
        return log_time_info_data