from datetime import datetime

from cassandra.cqlengine import columns, models

from utils import timemanager

class Quality_controls(models.Model):
    bucket = columns.Integer(primary_key=True, default=0)
    qc_level = columns.Integer(primary_key=True, clustering_order="ASC")
    qc_name = columns.Text()
    qc_description = columns.Text()

    @classmethod
    def get_all_qcs(cls):
        """Return all quality controls or an empty list if not found. """
        qcs_data = []
        all_qcs_query = Quality_controls.objects.filter(bucket=0)
        for row in all_qcs_query:
            qc = {
                'qc_level' : row.qc_level,
                'qc_name' : row.qc_name,
                'qc_description' : row.qc_description,
            }
            qcs_data.append(qc)
        return qcs_data

class Quality_control_info_by_quality_control(models.Model):
    qc_level = columns.Integer(primary_key=True)
    qc_name = columns.Text()
    qc_description = columns.Text()

    @classmethod
    def get_qc(cls, qc_level):
        """
        Return quality control or an empty list if not found.

        Keyword arguments:
        qc_level -- qc identifier (int)
        """
        qc_data = []
        qc_query = Quality_control_info_by_quality_control.objects.filter(qc_level=qc_level)
        for row in qc_query:
            qc = {
                'qc_name' : row.qc_name,
                'qc_description' : row.qc_description
            }
            qc_data.append(qc)
        return qc_data

class Quality_control_level_info_by_log(models.Model):
    log_id = columns.UUID(primary_key=True, partition_key=True)
    qc_level = columns.Integer(primary_key=True, clustering_order="ASC")
    qc_name = columns.Text()
    qc_replacement_value = columns.Float()

    @classmethod
    def get_log_qc_levels(cls, log_id, **qc_levels):
        """
        Return log quality control levels or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        qc_level -- qc identifier (int)
        """
        log_qc_levels_data = []
        log_qc_schedule_query = Quality_control_level_info_by_log.objects.filter(log_id=log_id)
        if qc_levels:
            if (len(qc_levels) == 1):
                #  Only one timestamp given
                if (qc_levels.get('eq_level')):
                    # Equal to (=) timestamp
                    qc_level = qc_levels.get('eq_level')
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level == qc_level)
                elif (qc_levels.get('lt_level')):
                    # Less than (<) timestamp
                    qc_level = qc_levels.get('lt_level')
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level < qc_level)
                elif (qc_levels.get('lte_level')):
                    # Less than or equal to (<=) timestamp
                    qc_level = qc_levels.get('lte_level')
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level <= qc_level)
                elif (qc_levels.get('gt_level')):
                    # Greater than (>) timestamp
                    qc_level = qc_levels.get('gt_level')
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level > qc_level)
                elif (qc_levels.get('gte_level')):
                    # Greater than or equal to (>=) timestamp
                    qc_level = qc_levels.get('gte_level')
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level >= qc_level)
            else:
                #  Two timestamps given
                if (qc_levels.get('lt_level') and qc_levels.get('gt_level')):
                    # Less than (<) and greater than (>) timestamp
                    to_qc_level = qc_levels.get('lt_level')
                    from_qc_level = qc_levels.get('gt_level')
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level < to_qc_level)
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level > from_qc_level)
                if (qc_levels.get('lte_level') and qc_levels.get('gte_level')):
                    # Less than or equal to (<=) and greater than or equal to (>=) timestamp
                    to_qc_level = qc_levels.get('lte_level')
                    from_qc_level = qc_levels.get('gte_level')
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level <= to_qc_level)
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level >= from_qc_level)
                if (qc_levels.get('lt_level') and qc_levels.get('gte_level')):
                    # Less than (<) and greater than or equal to (>=) timestamp
                    to_qc_level = qc_levels.get('lt_level')
                    from_qc_level = qc_levels.get('gte_level')
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level < to_qc_level)
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level >= from_qc_level)
                if (qc_levels.get('lte_level') and qc_levels.get('gt_level')):
                    # Less than or equal to (<=) and greater than (>) timestamp
                    to_qc_level = qc_levels.get('lte_level')
                    from_qc_level = qc_levels.get('gt_level')
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level <= to_qc_level)
                    log_qc_schedule_query.filter(Quality_control_level_info_by_log.qc_level > from_qc_level)
        for row in log_qc_schedule_query:
            qc = {
                'qc_level' : row.qc_level,
                'qc_name' : row.qc_name,
                'qc_replacement_value' : row.qc_replacement_value
            }
            log_qc_levels_data.append(qc)
        return log_qc_levels_data

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

    @classmethod
    def get_log_qc_values(cls, log_id, qc_level, json_request=None, **months):
        """
        Return log quality control values to be used for performing various quality controls,
        or return an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        qc_level -- qc identifier (int)
        json_request -- if true, convert datetime to timestamp representation (bool).
        months -- if given, get a specific month or range of months to be used for performing seasonal quality control (datetime).
        """
        log_qc_info_data = []
        log_qc_info_query = cls.objects.filter(log_id=log_id, qc_level=qc_level)
        if months:
            if (len(months) == 1):
                #  Only one timestamp given
                if (months.get('eq_timestamp')):
                    # Equal to (=) timestamp
                    timestamp = months.get('eq_timestamp')
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day == timestamp)
                elif (months.get('lt_timestamp')):
                    # Less than (<) timestamp
                    timestamp = months.get('lt_timestamp')
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day < timestamp)
                elif (months.get('lte_timestamp')):
                    # Less than or equal to (<=) timestamp
                    timestamp = months.get('lte_timestamp')
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day <= timestamp)
                elif (months.get('gt_timestamp')):
                    # Greater than (>) timestamp
                    timestamp = months.get('gt_timestamp')
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day > timestamp)
                elif (months.get('gte_timestamp')):
                    # Greater than or equal to (>=) timestamp
                    timestamp = months.get('gte_timestamp')
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day >= timestamp)
            else:
                #  Two timestamps given
                if (months.get('lt_timestamp') and months.get('gt_timestamp')):
                    # Less than (<) and greater than (>) timestamp
                    to_timestamp = months.get('lt_timestamp')
                    from_timestamp = months.get('gt_timestamp')
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day < to_timestamp)
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day > from_timestamp)
                if (months.get('lte_timestamp') and months.get('gte_timestamp')):
                    # Less than or equal to (<=) and greater than or equal to (>=) timestamp
                    to_timestamp = months.get('lte_timestamp')
                    from_timestamp = months.get('gte_timestamp')
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day <= to_timestamp)
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day >= from_timestamp)
                if (months.get('lt_timestamp') and months.get('gte_timestamp')):
                    # Less than (<) and greater than or equal to (>=) timestamp
                    to_timestamp = months.get('lt_timestamp')
                    from_timestamp = months.get('gte_timestamp')
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day < to_timestamp)
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day >= from_timestamp)
                if (months.get('lte_timestamp') and months.get('gt_timestamp')):
                    # Less than or equal to (<=) and greater than (>) timestamp
                    to_timestamp = months.get('lte_timestamp')
                    from_timestamp = months.get('gt_timestamp')
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day <= to_timestamp)
                    log_qc_info_query = log_qc_info_query.filter(Quality_control_info_by_log.month_first_day > from_timestamp)

        for row in log_qc_info_query:
            if json_request:
                if (row.month_first_day == datetime.utcfromtimestamp(0)):
                    month_first_day = None
                else:
                    tm = timemanager.TimeManager()
                    month_first_day = tm.json_date_handler(row.month_first_day)
            else:
                month_first_day = row.month_first_day
            qc = {
                'month_first_day' : month_first_day,
                'qc_parameters' : row.qc_parameters,
                'qc_time_interval' : row.qc_time_interval,
                'qc_parameters_min_values' : row.qc_parameters_min_values,
                'qc_parameters_max_values' : row.qc_parameters_max_values,
                'qc_window_sizes' : row.qc_window_sizes,
                'qc_replacement_value' : row.qc_replacement_value
            }
            log_qc_info_data.append(qc)
        return log_qc_info_data

class Log_quality_control_schedule_by_log(models.Model):
    log_id = columns.UUID(primary_key=True)
    qc_level = columns.Integer(primary_key=True, clustering_order="ASC")
    log_qc_interval = columns.Text(default=None)
    log_last_quality_control = columns.DateTime(default=None)
    log_next_quality_control = columns.DateTime(default=None)

    @classmethod
    def get_log_qc_schedule(cls, log_id, **qc_levels):
        """
        Return log quality control info or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        qc_level -- qc identifier (int)
        """
        log_qc_schedule_info_data = []
        log_qc_schedule_info_query = cls.objects.filter(log_id=log_id)
        if qc_levels:
            if (len(qc_levels) == 1):
                #  Only one timestamp given
                if (qc_levels.get('eq_level')):
                    # Equal to (=) timestamp
                    qc_level = qc_levels.get('eq_level')
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level == qc_level)
                elif (qc_levels.get('lt_level')):
                    # Less than (<) timestamp
                    qc_level = qc_levels.get('lt_level')
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level < qc_level)
                elif (qc_levels.get('lte_level')):
                    # Less than or equal to (<=) timestamp
                    qc_level = qc_levels.get('lte_level')
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level <= qc_level)
                elif (qc_levels.get('gt_level')):
                    # Greater than (>) timestamp
                    qc_level = qc_levels.get('gt_level')
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level > qc_level)
                elif (qc_levels.get('gte_level')):
                    # Greater than or equal to (>=) timestamp
                    qc_level = qc_levels.get('gte_level')
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level >= qc_level)
            else:
                #  Two timestamps given
                if (qc_levels.get('lt_level') and qc_levels.get('gt_level')):
                    # Less than (<) and greater than (>) timestamp
                    to_qc_level = qc_levels.get('lt_level')
                    from_qc_level = qc_levels.get('gt_level')
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level < to_qc_level)
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level > from_qc_level)
                if (qc_levels.get('lte_level') and qc_levels.get('gte_level')):
                    # Less than or equal to (<=) and greater than or equal to (>=) timestamp
                    to_qc_level = qc_levels.get('lte_level')
                    from_qc_level = qc_levels.get('gte_level')
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level <= to_qc_level)
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level >= from_qc_level)
                if (qc_levels.get('lt_level') and qc_levels.get('gte_level')):
                    # Less than (<) and greater than or equal to (>=) timestamp
                    to_qc_level = qc_levels.get('lt_level')
                    from_qc_level = qc_levels.get('gte_level')
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level < to_qc_level)
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level >= from_qc_level)
                if (qc_levels.get('lte_level') and qc_levels.get('gt_level')):
                    # Less than or equal to (<=) and greater than (>) timestamp
                    to_qc_level = qc_levels.get('lte_level')
                    from_qc_level = qc_levels.get('gt_level')
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level <= to_qc_level)
                    log_qc_schedule_info_query.filter(Log_quality_control_schedule_by_log.qc_level > from_qc_level)

        for row in log_qc_schedule_info_query:
            qc = {
                'qc_level' : row.qc_level,
                'log_qc_interval' : row.log_qc_interval,
                'log_last_quality_control' : row.log_last_quality_control,
                'log_next_quality_control' : row.log_next_quality_control
            }
            log_qc_schedule_info_data.append(qc)
        return log_qc_schedule_info_data