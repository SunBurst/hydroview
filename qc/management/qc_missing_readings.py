import configparser
import datetime
from utils import timemanager


def find_missing_readings_by_time(parameter, sensor, from_ts_utc, to_ts_utc):	

    """ Scans for missing sites for a given parameter and sensor on a given timerange.
    Args: parameter (string): the parameter of interest.
          sensor (string): the sensor of interest.
          timerange (list): check on the given timestamp interval. """

    tm = TimeManager()
    replacement_val = config_parser_qc.get('QC_PARAMS', 'repl_missing_value')
    minute_intervals = int(config_parser_qc.get('QC_MINUTES_BETWEEN_READINGS', sensor)
    from_ts = from_ts_utc
    to_ts = to_ts_utc
    from_dt = tm.timestamp_to_datetime_utc(from_ts/1e3)
    to_dt = tm.timestamp_to_datetime_utc(to_ts/1e3)
    temp_dt = to_dt
    time_reference = []
    time_reading = []

    while(temp_dt > from_dt):
        previous_dt = temp_dt - datetime.timedelta(minutes=minute_intervals)
        temp_dt = previous_dt
        time_reference.append(temp_dt)

    try:
        print("Fetching rows with attributes ", sensor, parameter, from_dt, to_dt)
        values = [sensor, parameter, from_ts, to_ts]
        query_params = [values]
        rows = db.get_readings_by_sensor_range(query_params)

        for row in rows:
            time_reading.append(row.time)

    except:
        db.cluster_disconnect()
        print("Query timed out..")

    missing_readings = list(set(time_reference).difference(time_reading))
    msg = 'Missing sites QC on parameter "%s" completed.' % parameter
    
    if missing_readings:
        missing_rows = []
        num_of_rep_values = 0
        for repl_utc_dt in missing_readings:
            utc_ts_millis = tm.utc_dt_to_utc_ts_millis(repl_utc_dt)
            missing_rows.append([sensor, parameter, utc_ts_millis, replacement_val])
            num_of_rep_values += 1
        
        db.store_reading(missing_rows)
		msg += ' %s rows inserted.' % num_of_rep_values
    else:
        msg += ' No rows inserted.'

    print(msg)