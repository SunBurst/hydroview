from cassandra.cqlengine import columns, models

from utils import tools

class Logger_time_formats(models.Model):
    bucket = columns.Integer(primary_key=True, default=0)
    logger_time_format_id = columns.UUID(primary_key=True)
    logger_time_format_name = columns.Text(primary_key=True, clustering_order="ASC")
    logger_time_format_description = columns.Text(default=None)

    @classmethod
    def get_all_logger_time_formats(cls, json_request=None):
        """Return all logger time formats or an empty list if not found.

        Keyword arguments:
        json_request -- if true, convert uuid to string representation (bool).
        """
        logger_time_formats_data = []
        all_time_formats_query = cls.objects.filter(bucket=0)
        for row in all_time_formats_query:
            if json_request:
                logger_time_format_id = tools.MiscTools.uuid_to_str(row.logger_time_format_id)
            else:
                logger_time_format_id = row.logger_time_format_id
            time_format = {
                'logger_time_format_id' : logger_time_format_id,
                'logger_time_format_name' : row.logger_time_format_name,
                'logger_time_format_description' : row.logger_time_format_description,
            }
            logger_time_formats_data.append(time_format)
        return logger_time_formats_data

class Logger_time_format_by_logger_time_format(models.Model):
    logger_time_format_id =  columns.UUID(primary_key=True)
    logger_time_format_name = columns.Text()
    logger_time_format_description = columns.Text(default=None)
    logger_time_ids = columns.List(columns.Text)
    logger_time_id_types = columns.Map(columns.Text, columns.Text)

    @classmethod
    def get_logger_time_format(cls, logger_time_format_id):
        """
        Return logger time format or an empty list if not found.

        Keyword arguments:
        logger_time_format_id -- logger time format (UUID)
        """
        logger_time_formats_data = []
        time_format_query = cls.objects.filter(logger_time_format_id=logger_time_format_id)
        for row in time_format_query:
            time_format = {
                'logger_time_format_name' : row.logger_time_format_name,
                'logger_time_format_description' : row.logger_time_format_description,
                'logger_time_ids' : row.logger_time_ids,
                'logger_time_id_types' : row.logger_time_id_types
            }
            logger_time_formats_data.append(time_format)
        return logger_time_formats_data

class Logs_by_logger_time_format(models.Model):
    logger_time_format_id = columns.UUID(primary_key=True)
    log_id = columns.UUID(primary_key=True, clustering_order="ASC")

    @classmethod
    def get_logs_by_logger_time_format(cls, logger_time_format_id):
        """
        Return logs using the given logger time format or an empty list if not found.

        Keyword arguments:
        logger_time_format_id -- logger time format (UUID)
        """
        logs_data = []
        all_logs_query = cls.objects.filter(logger_time_format_id=logger_time_format_id)
        for row in all_logs_query:
            log = {
                'log_id' : row.log_id
            }
            logs_data.append(log)
        return logs_data
