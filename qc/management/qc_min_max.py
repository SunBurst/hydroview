import calendar
import configparser
from collections import defaultdict

import utils.dbmanager as db

def utc_dt_to_utc_ts_millis(utc_dt):
    utc_ts = int(calendar.timegm(utc_dt.timetuple()))
    utc_ts_millis = utc_ts*1000
    return utc_ts_millis

def value_pass(value, min_val, max_val):
    if min_val <= value <= max_val:
        return True
    else:
        return False

def min_max_on_row(row, thresholds, rep_val):
    min_value = thresholds[0]
    max_value = thresholds[1]

    if not (value_pass(row.value, min_value, max_value)) and row.value != rep_val:
        #utc_ts = int(calendar.timegm(row.time.timetuple()))
        #utc_ts_millis = utc_ts*1000
        utc_ts_millis = utc_dt_to_utc_ts_millis(row.time)
        update_row = [row.sensor, row.parameter, str(utc_ts_millis), rep_val]
        return update_row
    else:
        return []

def run_min_max(query_params, min_max_thresholds):
    replacement_val = config_parser_qc.get('QC_PARAMS', 'repl_val_min_max')
    if replacement_val:
        replacement_val = float(replacement_val)
        try:
            rows = db.get_readings_by_sensor_range(query_params)
            rows_to_replace = []

            if rows:
                for row in rows:
                    if (row.parameter in min_max_thresholds):
                        param_min_max_thresholds = min_max_thresholds[row.parameter]
                        update_row = min_max_on_row(row, param_min_max_thresholds, replacement_val)
                        if update_row:
                            rows_to_replace.append(update_row)
        except:
            print("QC min max query timed out..")
            db.cluster_disconnect()
    else:
        print("No replacement value found for min max QC test!")

    if rows_to_replace:
        print(rows_to_replace)
        try:
            db.store_reading(rows_to_replace)
            print("QC min max completed. ", len(rows_to_replace) + " rows replaced!")
        except:
            print("Failed to replace exceeding rows in min max QC")
    else:
        print("QC min max completed. No rows replaced!")

def qc_min_max_on_sensor(from_ts_utc, to_ts_utc, sensor_name)
    """
    """
    qc_params = [key for key in config_parser_qc.get('QC_MIN_THRESHOLDS')]
    qc_mins = [float(val) for key, val in config_parser_qc.get('QC_MIN_THRESHOLDS').items()]
    qc_maxes = [float(val) for key, val in config_parser_qc.get('QC_MAX_THRESHOLDS').items()]	
    qc_values = [[qc_mins[x],qc_maxes[x]] for x in range(len(qc_mins))]
    qc_thresholds = dict(zip(qc_params,qc_values))            
    query_min_max_params = []

    for param in params:
        if (param in qc_thresholds):
            print('QC min max on parameter "%s" with sensor name "%s"' % (param, sensor_name))
            temp_query_params = [sensor_name, param, from_ts_utc, to_ts_utc]
            query_min_max_params.append(temp_query_params)	

    if query_min_max_params:
        run_min_max(query_min_max_params, qc_thresholds)
		
    return
					
