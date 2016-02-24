import datetime as dt
import os, time
from collections import defaultdict
from operator import itemgetter

from cassandra.cqlengine.management import sync_table

from sites.models import Parameters_by_sensor, Sensor_info_by_sensor
from sites.sensors import SensorData
from utils import timemanager

def split_campbell_file(sensor_name, file_path, time_zone, time_ids, parameters, last_line_num=None, load_data=None):

    def _split_current_line(_sensor_name, current_line, tm, time_params):
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
            param_reading = [_sensor_name, parameter, utc_dt, param_value]
            readings_params_dict[parameter].append(param_reading)

    folder_path,file = os.path.split(os.path.abspath(file_path))
    file_ext = os.path.splitext(os.path.abspath(file_path))[1]  #: e.g. .dat

    readings_params_dict = defaultdict(list)
    temp_params_dict = defaultdict(list)
    num_new_readings = 0
    raw_time_manager = timemanager.RawTimeManager(time_zone)
    allocated_time_params = raw_time_manager.count_time_id_params(time_ids)

    if load_data:
        for line_number, line in enumerate(load_data):
            _split_current_line(sensor_name, line, raw_time_manager, allocated_time_params)
    else:
        with open(file_path) as f_in:
            f_list = [line.rstrip('\n') for line in f_in]
        for line_number, line in enumerate(f_list):
            if (last_line_num < line_number):
                _split_current_line(sensor_name, line, raw_time_manager, allocated_time_params)

    for parameter, readings_list in readings_params_dict.items():
        target_parameter_file = os.path.join(os.path.abspath(folder_path), 'parameters', parameter + file_ext)
        os.makedirs(os.path.dirname(target_parameter_file), exist_ok=True)

        with open(target_parameter_file, 'a+') as f_out:
            for row in readings_list:
                num_new_readings += 1
                temp_params_dict[parameter].append(row)
                f_out.write("%s\n" % (row))

    print('Finished splitting file "%s".' % file)
    print("Sorting sites in order to optimize database insertion..")
    for parameter, readings_list in temp_params_dict.items():
        sorted(readings_list, key=itemgetter(1)) #: Sort by second element, i.e. sensor name.
    return num_new_readings, temp_params_dict


def run_sensor_update(sensor_name, sensor_info):
    file_path = sensor_info.get('file_path')
    last_line_num = sensor_info.get('file_line_num')
    time_format = sensor_info.get('time_format')
    time_zone = sensor_info.get('time_zone')
    parameters = sensor_info.get('parameters')

    if(time_format == 'campbell'):
        time_ids = sensor_info.get('time_ids')
        if file_path:
            num_new_readings = 0
            new_rows_dict = defaultdict(list)
            if (not last_line_num or last_line_num == 0):   #: Split whole file.
                with open(file_path) as f_in:
                    load_data = [line.rstrip('\n') for line in f_in]    #: Read whole file into memory.
                    num_new_readings, new_rows_dict = split_campbell_file(sensor_name, file_path, time_zone, time_ids, parameters, last_line_num, load_data)
            else:
                load_data = None
                num_new_readings, new_rows_dict = split_campbell_file(sensor_name, file_path, time_zone, time_ids, parameters, last_line_num, load_data)
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
                                print(row[0], row[1], row[2], row[3])
                                Parameters_by_sensor.create(sensor=row[0], qc_level=0, parameter=row[1], time=row[2], value=row[3])
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

def check_sensor_update(sensor_name):

    sync_table(Sensor_info_by_sensor)
    sensor_data = SensorData.get_sensor(sensor_name)
    sensor_info = sensor_data[0]

    if(sensor_info.get('next_update')):
        run_sensor_update(sensor_name, sensor_info)
    else:
        return

def prepare_sensor_update(sensor_name, update_time):

    while True:
        now = dt.datetime.now()
        target = update_time
        print(target)
        if target < now:
            check_sensor_update(sensor_name)
        else:
            time.sleep((target-now).total_seconds())

