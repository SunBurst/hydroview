from .models import Quality_controls, Quality_control_info_by_quality_control, Quality_control_level_by_log, \
    Quality_control_info_by_log

class QCData(object):
    """Helper class for getting quality control related data from the Cassandra database. """

    @classmethod
    def get_all_qcs(cls):
        """Return all quality controls or an empty list if not found. """
        qcs_data = []
        all_qcs_query = Quality_controls.objects.filter(bucket=0)
        for row in all_qcs_query:
            qc = {
                'qc_level' : row.qc_level,
                'qc_name' : row.qc_name,
                'description' : row.description,
            }
            qcs_data.append(qc)
        return qcs_data

    @classmethod
    def get_qc(cls, qc_level):
        """
        Return quality control or an empty list if not found.

        Keyword arguments:
        qc_level -- qc identifier (int)
        """
        qc_data = []
        qc_query = Quality_control_info_by_quality_control.objects.filter(site_id=qc_level)
        for row in qc_query:
            qc = {
                'qc_name' : row.qc_name,
                'qc_description' : row.qc_description,
                'qc_replacement_value' : row.qc_replacement_value,
            }
            qc_data.append(qc)
        return qc_data

    @classmethod
    def get_log_qc_levels(cls, log_id, qc_level=None):
        """
        Return log quality control levels or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        qc_level -- qc identifier (int)
        """
        log_qc_levels_data = []
        log_qc_levels_query = Quality_control_level_by_log.objects.filter(log_id=log_id)
        if qc_level:
            log_qc_levels_query.filter(qc_level=qc_level)
        for row in log_qc_levels_query:
            qc = {
                'qc_level' : row.qc_level,
                'qc_name' : row.qc_name,
                'qc_replacement_value' : row.qc_replacement_value
            }
            log_qc_levels_data.append(qc)
        return log_qc_levels_data

    @classmethod
    def get_log_qc_info(cls, log_id, qc_level=None):
        """
        Return log quality control info or an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        qc_level -- qc identifier (int)
        """
        log_qc_info_data = []
        log_qc_info_query = Quality_control_level_by_log.objects.filter(log_id=log_id)
        if qc_level:
            log_qc_info_query.filter(qc_level=qc_level)
        for row in log_qc_info_query:
            qc = {
                'qc_level' : row.qc_level,
                'last_quality_control' : row.last_quality_control,
                'next_quality_control' : row.next_quality_control
            }
            log_qc_info_data.append(qc)
        return log_qc_info_data

    @classmethod
    def get_log_qc_level(cls, log_id, qc_level, **months):
        """
        Return log quality control info to be used for performing various quality controls,
        or return an empty list if not found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        qc_level -- qc identifier (int)
        month_first_day -- if given, get a specific month to be used for performing seasonal quality control.
        """

        log_qc_info_data = []
        log_qc_info_query = Quality_control_level_by_log.objects.filter(log_id=log_id, qc_level=qc_level)
        if months:
            if (len(months) == 1):
                #  Only one timestamp given
                if (months.get('eq_timestamp')):
                    # Equal to (=) timestamp
                    timestamp = months.get('eq_timestamp')
                    log_qc_info_query.filter(Quality_control_level_by_log.time == timestamp)
                elif (months.get('lt_timestamp')):
                    # Less than (<) timestamp
                    timestamp = months.get('lt_timestamp')
                    log_qc_info_query.filter(Quality_control_level_by_log.time < timestamp)
                elif (months.get('lte_timestamp')):
                    # Less than or equal to (<=) timestamp
                    timestamp = months.get('lte_timestamp')
                    log_qc_info_query.filter(Quality_control_level_by_log.time <= timestamp)
                elif (months.get('gt_timestamp')):
                    # Greater than (>) timestamp
                    timestamp = months.get('gt_timestamp')
                    log_qc_info_query.filter(Quality_control_level_by_log.time > timestamp)
                elif (months.get('gte_timestamp')):
                    # Greater than or equal to (>=) timestamp
                    timestamp = months.get('gte_timestamp')
                    log_qc_info_query.filter(Quality_control_level_by_log.time >= timestamp)
            else:
                #  Two timestamps given
                if (months.get('lt_timestamp') and months.get('gt_timestamp')):
                    # Less than (<) and greater than (>) timestamp
                    to_timestamp = months.get('lt_timestamp')
                    from_timestamp = months.get('gt_timestamp')
                    log_qc_info_query.filter(Quality_control_level_by_log.time < to_timestamp)
                    log_qc_info_query.filter(Quality_control_level_by_log.time > from_timestamp)
                if (months.get('lte_timestamp') and months.get('gte_timestamp')):
                    # Less than or equal to (<=) and greater than or equal to (>=) timestamp
                    to_timestamp = months.get('lte_timestamp')
                    from_timestamp = months.get('gte_timestamp')
                    log_qc_info_query.filter(Quality_control_level_by_log.time <= to_timestamp)
                    log_qc_info_query.filter(Quality_control_level_by_log.time >= from_timestamp)
                if (months.get('lt_timestamp') and months.get('gte_timestamp')):
                    # Less than (<) and greater than or equal to (>=) timestamp
                    to_timestamp = months.get('lt_timestamp')
                    from_timestamp = months.get('gte_timestamp')
                    log_qc_info_query.filter(Quality_control_level_by_log.time < to_timestamp)
                    log_qc_info_query.filter(Quality_control_level_by_log.time >= from_timestamp)
                if (months.get('lte_timestamp') and months.get('gt_timestamp')):
                    # Less than or equal to (<=) and greater than (>) timestamp
                    to_timestamp = months.get('lte_timestamp')
                    from_timestamp = months.get('gt_timestamp')
                    log_qc_info_query.filter(Quality_control_level_by_log.time <= to_timestamp)
                    log_qc_info_query.filter(Quality_control_level_by_log.time > from_timestamp)

        for row in log_qc_info_query:
            qc = {
                'month_first_day' : row.month_first_day,
                'qc_parameters' : row.qc_parameters,
                'qc_minute_interval' : row.qc_minute_interval,
                'qc_parameters_min_values' : row.qc_parameters_min_values,
                'qc_parameters_max_values' : row.qc_parameters_max_values,
                'qc_window' : row.qc_window,
                'qc_replacement_value' : row.qc_replacement_value
            }
            log_qc_info_data.append(qc)
        return log_qc_info_data



