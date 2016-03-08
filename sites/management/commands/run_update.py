import datetime as dt
import os
from collections import defaultdict
from operator import itemgetter

from cassandra.cqlengine.management import sync_table

from sites.models import Parameters_readings_by_log
from sites.loggers import LoggerData
from sites.logs import LogData
from utils import timemanager

def split_campbell_file(log_id, file_path, time_zone, time_ids, parameters, reading_types, last_line_num=None, load_data=None):

    def _split_current_line(_log_id, current_line, tm, time_params):
        """ Helper function to break current row to each corresponding parameter file.
            Args: current_line (string): The row to process.
        """
        current_line_as_list = current_line.strip().split(',')
        #sensor_id = identify_sensor_id(current_line_as_list)

        #sensor_name = config_parser.get('SENSOR_IDS', sensor_id)
        #raw_file_params_order_list = config_parser.get('RAW_FILE_ORDERS', sensor_name).split(',')
        #time_identifiers_list = config_parser.get('TIME_IDENTIFIERS', sensor_name).split(',')		#: Year, julianday, hour (minute)

        #ts = tm.raw_format_to_timestamp(current_line_as_list, time_identifiers_list)    #: WORKS FOR RAW QUERIES
        #ts_as_string = str(ts)    #: WORKS FOR RAW QUERIES

        utc_dt = tm.raw_format_to_timestamp(current_line_as_list, time_ids)
        indexes = []														#: Replace raw time identifiers with timestamp representation.
        for i in range(time_params):
            indexes.append(i+1)

        for index in sorted(indexes, reverse = True):
            del current_line_as_list[index]

        del current_line_as_list[0]

        for parameter, val in zip(parameters, current_line_as_list):
            #val_as_string = str(val)    #: WORKS FOR RAW QUERIES
            #values = ','.join([sensor_name, parameter, ts_as_string, val_as_string])		#: WORKS FOR RAW QUERIES
            param_value = float(val)
            param_reading = [_log_id, parameter, 0, utc_dt, param_value]
            readings_params_dict[parameter].append(param_reading)

    folder_path, file = os.path.split(os.path.abspath(file_path))
    file_ext = os.path.splitext(os.path.abspath(file_path))[1]  #: e.g. .dat

    readings_params_dict = defaultdict(list)
    temp_params_dict = defaultdict(list)
    num_new_readings = 0
    raw_time_manager = timemanager.RawTimeManager(time_zone)
    allocated_time_params = raw_time_manager.count_time_id_params(time_ids)

    if load_data:
        for line_number, line in enumerate(load_data):
            _split_current_line(log_id, line, raw_time_manager, allocated_time_params)
    else:
        with open(file_path) as f_in:
            f_list = [line.rstrip('\n') for line in f_in]
        for line_number, line in enumerate(f_list):
            if (last_line_num < line_number):
                _split_current_line(log_id, line, raw_time_manager, allocated_time_params)

    for parameter, readings_list in readings_params_dict.items():
        target_parameter_file = os.path.join(os.path.abspath(folder_path), 'parameters level 0', parameter + file_ext)
        os.makedirs(os.path.dirname(target_parameter_file), exist_ok=True)

        with open(target_parameter_file, 'a+') as f_out:
            for row in readings_list:
                num_new_readings += 1
                temp_params_dict[parameter].append(row)
                log_id = row[0]
                param_name = row[1]
                qc_level = row[2]
                time_str = str(row[3])
                value = row[4]
                f_out.write(u"{0} {1} {2} {3} {4}\n".format(
                    log_id,
                    param_name,
                    qc_level,
                    time_str,
                    value
                ))

    print('Finished splitting file "%s".' % file)
    print("Sorting sites in order to optimize database insertion..")
    for parameter, readings_list in temp_params_dict.items():
        sorted(readings_list, key=itemgetter(1)) #: Sort by second element, i.e. log_id.
    return num_new_readings, temp_params_dict


def run_log_update(log_id, log_update_info, log_time_info, log_parameters_info):
    log_file_path = log_update_info.get('log_file_path')
    log_last_line_num = log_update_info.get('log_file_line_num')
    logger_time_format = log_time_info.get('logger_time_format')
    log_time_zone = log_time_info.get('log_time_zone')
    log_parameters = log_parameters_info.get('log_parameters')
    log_reading_types = log_parameters_info.get('log_reading_types')

    if(logger_time_format == 'Campbell-Legacy'):
        log_time_ids = log_time_info.get('log_time_ids')
        if log_file_path:
            num_new_readings = 0
            new_rows_dict = defaultdict(list)
            if (not log_last_line_num or log_last_line_num == 0):   #: Split whole file.
                with open(log_file_path) as f_in:
                    load_data = [line.rstrip('\n') for line in f_in]    #: Read whole file into memory.
                    num_new_readings, new_rows_dict = split_campbell_file(
                        log_id, log_file_path, log_time_zone,
                        log_time_ids, log_parameters, log_reading_types, log_last_line_num, load_data
                    )
            else:
                load_data = None
                num_new_readings, new_rows_dict = split_campbell_file(
                    log_id, log_file_path, log_time_zone, log_time_ids,
                    log_parameters, log_reading_types, log_last_line_num, load_data
                )
            print('Updated parameter files with %s new sites.' % num_new_readings)
            print("File updating done!")
            if new_rows_dict:
                print("Beginning database insertion..")
                try:
                    #raw_queries.store_readings_concurrently(session, new_rows)
                            #self.store_readings(session, cluster, new_rows)
                    for param, sites in new_rows_dict.items():
                        #batch = []
                        for i, row in enumerate(sites):
                            try:
                                print(row[0], row[1], row[2], row[3], row[4])
                                Parameters_readings_by_log.create(
                                    log_id=row[0],
                                    reading_parameter=row[1],
                                    reading_qc_level=row[2],
                                    reading_time=row[3],
                                    reading_value=row[4]
                                )
                            except:
                                print("Query timed out..")
                                    #cluster.shutdown()
                                #batch.append(row)
                            #db.store_reading(batch)
                except:
                    print('Query timed out! Shutting down session..')
               #             cluster.shutdown()
               #         logging.info('Successfully inserted "%s" new sites!' % num_new_readings)
                #self.stdout.write(self.style.SUCCESS('Successfully inserted "%s" new sites!' % num_new_readings))
        else:
            print("no file path set!")
    else:
        print("Other formats are not supported yet!")

#def check_sensor_update(sensor_name):

#    sync_table(Sensor_info_by_sensor)
#    sensor_data = LogData.get_sensor(sensor_name)
#    sensor_info = sensor_data[0]

#    if(sensor_info.get('next_update')):
#        run_sensor_update(sensor_name, sensor_info)
#    else:
#        return

if __name__=='__main__':
    #check_sensor_update('Malma Island Daily')
    log_id = '9d0cca9a-cb33-4bdd-bc8c-4fbe3c82e882'
    log_update_info = LogData.get_log_update_info(log_id)
    log_time_info = LoggerData.get_log_time_info(log_id)
    log_parameters = LogData.get_log_parameters(log_id)
    run_log_update(log_id, log_update_info, log_time_info, log_parameters)
#def prepare_sensor_update(sensor_name, update_time):

    #while True:
    #    now = dt.datetime.now()
    #    target = update_time
    #    print(target)
    #    if target < now:
    #        check_sensor_update(sensor_name)
    #    else:
    #        time.sleep((target-now).total_seconds())

