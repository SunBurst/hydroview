from .models import Parameters_readings_by_log, Profiles_readings_by_log, Status_parameter_readings_by_log

class ReadingData(object):
    """Helper class for getting reading related data from the Cassandra database. """

    @classmethod
    def get_parameter_readings(cls, log_id, qc_level, parameter, **time):
        """
        Return readings for a specific log with a given quality control level and parameter name on a given time range,
        or return an empty list if no readings were found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        qc_level -- quality control level, starting on level 0 (raw data) (int)
        parameter -- name of parameter (str)
        time -- if not given, get all parameter readings. If given only from_timestamp, perform range query from this
                timestamp. If given only to_timestamp, perform range query to this timestamp. If given both from_timestamp and
                to_timestamp, perform range query between these timestamps (datetime).
        """
        parameter_readings_data = []
        parameter_readings_query = Parameters_readings_by_log.objects.filter(
                log_id=log_id, reading_qc_level=qc_level, reading_parameter=parameter
            )
        if time:
            if (len(time) == 1):
                #  Only one timestamp given
                if (time.get('eq_timestamp')):
                    # Equal to (=) timestamp
                    timestamp = time.get('eq_timestamp')
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time == timestamp)
                elif (time.get('lt_timestamp')):
                    # Less than (<) timestamp
                    timestamp = time.get('lt_timestamp')
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time < timestamp)
                elif (time.get('lte_timestamp')):
                    # Less than or equal to (<=) timestamp
                    timestamp = time.get('lte_timestamp')
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time <= timestamp)
                elif (time.get('gt_timestamp')):
                    # Greater than (>) timestamp
                    timestamp = time.get('gt_timestamp')
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time > timestamp)
                elif (time.get('gte_timestamp')):
                    # Greater than or equal to (>=) timestamp
                    timestamp = time.get('gte_timestamp')
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time >= timestamp)
            else:
                #  Two timestamps given
                if (time.get('lt_timestamp') and time.get('gt_timestamp')):
                    # Less than (<) and greater than (>) timestamp
                    to_timestamp = time.get('lt_timestamp')
                    from_timestamp = time.get('gt_timestamp')
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time < to_timestamp)
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time > from_timestamp)
                if (time.get('lte_timestamp') and time.get('gte_timestamp')):
                    # Less than or equal to (<=) and greater than or equal to (>=) timestamp
                    to_timestamp = time.get('lte_timestamp')
                    from_timestamp = time.get('gte_timestamp')
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time <= to_timestamp)
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time >= from_timestamp)
                if (time.get('lt_timestamp') and time.get('gte_timestamp')):
                    # Less than (<) and greater than or equal to (>=) timestamp
                    to_timestamp = time.get('lt_timestamp')
                    from_timestamp = time.get('gte_timestamp')
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time < to_timestamp)
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time >= from_timestamp)
                if (time.get('lte_timestamp') and time.get('gt_timestamp')):
                    # Less than or equal to (<=) and greater than (>) timestamp
                    to_timestamp = time.get('lte_timestamp')
                    from_timestamp = time.get('gt_timestamp')
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time <= to_timestamp)
                    parameter_readings_query.filter(Parameters_readings_by_log.reading_time > from_timestamp)

        for row in parameter_readings_query:
            reading = {
                'reading_time' : row.reading_time,
                'reading_value' : row.reading_value,
            }
            parameter_readings_data.append(reading)
        return parameter_readings_data

    @classmethod
    def get_profile_readings(cls, log_id, qc_level, profile, **time):
        """
        Return readings for a specific log with a given quality control level and profile name on a given time range,
        or return an empty list if no readings were found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        qc_level -- quality control level, starting on level 0 (raw data) (int)
        profile -- name of profile (str)
        time -- if not given, get all profile readings. If given only from_timestamp, perform range query from this
                timestamp. If given only to_timestamp, perform range query to this timestamp. If given both from_timestamp and
                to_timestamp, perform range query between these timestamps (datetime).
        """
        profile_readings_data = []
        profile_readings_query = Profiles_readings_by_log.objects.filter(
                log_id=log_id, reading_qc_level=qc_level, reading_profile=profile
            )
        if time:
            if (len(time) == 1):
                #  Only one timestamp given
                if (time.get('eq_timestamp')):
                    # Equal to (=) timestamp
                    timestamp = time.get('eq_timestamp')
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time == timestamp)
                elif (time.get('lt_timestamp')):
                    # Less than (<) timestamp
                    timestamp = time.get('lt_timestamp')
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time < timestamp)
                elif (time.get('lte_timestamp')):
                    # Less than or equal to (<=) timestamp
                    timestamp = time.get('lte_timestamp')
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time <= timestamp)
                elif (time.get('gt_timestamp')):
                    # Greater than (>) timestamp
                    timestamp = time.get('gt_timestamp')
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time > timestamp)
                elif (time.get('gte_timestamp')):
                    # Greater than or equal to (>=) timestamp
                    timestamp = time.get('gte_timestamp')
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time >= timestamp)
            else:
                #  Two timestamps given
                if (time.get('lt_timestamp') and time.get('gt_timestamp')):
                    # Less than (<) and greater than (>) timestamp
                    to_timestamp = time.get('lt_timestamp')
                    from_timestamp = time.get('gt_timestamp')
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time < to_timestamp)
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time > from_timestamp)
                if (time.get('lte_timestamp') and time.get('gte_timestamp')):
                    # Less than or equal to (<=) and greater than or equal to (>=) timestamp
                    to_timestamp = time.get('lte_timestamp')
                    from_timestamp = time.get('gte_timestamp')
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time <= to_timestamp)
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time >= from_timestamp)
                if (time.get('lt_timestamp') and time.get('gte_timestamp')):
                    # Less than (<) and greater than or equal to (>=) timestamp
                    to_timestamp = time.get('lt_timestamp')
                    from_timestamp = time.get('gte_timestamp')
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time < to_timestamp)
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time >= from_timestamp)
                if (time.get('lte_timestamp') and time.get('gt_timestamp')):
                    # Less than or equal to (<=) and greater than (>) timestamp
                    to_timestamp = time.get('lte_timestamp')
                    from_timestamp = time.get('gt_timestamp')
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time <= to_timestamp)
                    profile_readings_query.filter(Profiles_readings_by_log.reading_time > from_timestamp)

        for row in profile_readings_query:
            reading = {
                'reading_time' : row.reading_time,
                'reading_values' : row.reading_values,
            }
            profile_readings_data.append(reading)
        return profile_readings_data

    @classmethod
    def get_status_parameter_readings(cls, log_id, qc_level, parameter, **time):
        """
        Return readings for a specific log with a given quality control level and status parameter name on a given time range,
        or return an empty list if no readings were found.

        Keyword arguments:
        log_id -- log identifier (UUID)
        qc_level -- quality control level, starting on level 0 (raw data) (int)
        parameter -- name of status parameter (str)
        time -- if not given, get all status readings. If given only from_timestamp, perform range query from this
                timestamp. If given only to_timestamp, perform range query to this timestamp. If given both from_timestamp and
                to_timestamp, perform range query between these timestamps (datetime).
        """
        status_parameter_readings_data = []
        status_parameter_readings_query = Status_parameter_readings_by_log.objects.filter(
                log_id=log_id, reading_qc_level=qc_level, reading_parameter=parameter
            )
        if time:
            if (len(time) == 1):
                #  Only one timestamp given
                if (time.get('eq_timestamp')):
                    # Equal to (=) timestamp
                    timestamp = time.get('eq_timestamp')
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time == timestamp)
                elif (time.get('lt_timestamp')):
                    # Less than (<) timestamp
                    timestamp = time.get('lt_timestamp')
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time < timestamp)
                elif (time.get('lte_timestamp')):
                    # Less than or equal to (<=) timestamp
                    timestamp = time.get('lte_timestamp')
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time <= timestamp)
                elif (time.get('gt_timestamp')):
                    # Greater than (>) timestamp
                    timestamp = time.get('gt_timestamp')
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time > timestamp)
                elif (time.get('gte_timestamp')):
                    # Greater than or equal to (>=) timestamp
                    timestamp = time.get('gte_timestamp')
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time >= timestamp)
            else:
                #  Two timestamps given
                if (time.get('lt_timestamp') and time.get('gt_timestamp')):
                    # Less than (<) and greater than (>) timestamp
                    to_timestamp = time.get('lt_timestamp')
                    from_timestamp = time.get('gt_timestamp')
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time < to_timestamp)
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time > from_timestamp)
                if (time.get('lte_timestamp') and time.get('gte_timestamp')):
                    # Less than or equal to (<=) and greater than or equal to (>=) timestamp
                    to_timestamp = time.get('lte_timestamp')
                    from_timestamp = time.get('gte_timestamp')
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time <= to_timestamp)
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time >= from_timestamp)
                if (time.get('lt_timestamp') and time.get('gte_timestamp')):
                    # Less than (<) and greater than or equal to (>=) timestamp
                    to_timestamp = time.get('lt_timestamp')
                    from_timestamp = time.get('gte_timestamp')
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time < to_timestamp)
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time >= from_timestamp)
                if (time.get('lte_timestamp') and time.get('gt_timestamp')):
                    # Less than or equal to (<=) and greater than (>) timestamp
                    to_timestamp = time.get('lte_timestamp')
                    from_timestamp = time.get('gt_timestamp')
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time <= to_timestamp)
                    status_parameter_readings_query.filter(Status_parameter_readings_by_log.reading_time > from_timestamp)

        for row in status_parameter_readings_query:
            reading = {
                'reading_time' : row.reading_time,
                'reading_value' : row.reading_value,
            }
            status_parameter_readings_data.append(reading)
        return status_parameter_readings_data
