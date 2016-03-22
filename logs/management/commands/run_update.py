import os
import sys
from collections import defaultdict, OrderedDict
from operator import itemgetter
from datetime import datetime, timedelta

from cassandra.cqlengine import connection

from settings.base import CONFIG_PATH
from locations.models import Locations_by_site
from logs.models import Logs_by_location, Log_file_info_by_log, Log_info_by_log, Log_parameters_by_log, \
    Log_time_info_by_log, Log_update_schedule_by_log
from readings.models import Parameters_readings_by_log
from sites.models import Sites
from utils import logging, parser, timemanager

db_settings = parser.DatabaseSettingsParser('cassandra_config.ini')

connection.setup([db_settings.cassandra_host], db_settings.cassandra_keyspace)

class UpdateLog(object):


    def __init__(self, **kwargs):
        self.log_id = kwargs.get('log_id')
        self.log_name = kwargs.get('log_name')
        self.log_file_path = kwargs.get('log_file_path')
        self.log_file_line_num = kwargs.get('log_file_line_num')
        self.log_time_zone = kwargs.get('log_time_zone')
        self.log_time_ids = kwargs.get('log_time_ids')
        self.logger_time_formats = kwargs.get('logger_time_formats')
        self.log_parameters = kwargs.get('log_parameters')
        self.log_parameters_reading_types = kwargs.get('log_parameters_reading_types')

        self.log_data = self.load_file()
        self.process_data()

    def load_file(self):
        with open(self.log_file_path) as f_in:
            data = [line.rstrip('\n') for line in f_in]
        return data

    def process_row(self, row, raw_tm):

        row_as_list = row.strip().split(',')  #: list representation of current line.
        if (len(row_as_list) != len(self.log_parameters)):
            print("Parameter numbers doesn't match!")
            return

        row_time_ids = OrderedDict()
        parameter_readings = {}
        status_parameter_readings = {}
        profile_reading = {}

        for i, param in enumerate(self.log_parameters):
            if (self.log_parameters_reading_types.get(param) == 'ignore'):
                pass
            elif (self.log_parameters_reading_types.get(param) == 'time'):
                time_id_fmt = self.logger_time_formats.get(param)
                row_time_ids[time_id_fmt] = row_as_list[i]
            elif (self.log_parameters_reading_types.get(param) == 'parameter_reading'):
                parameter_readings[param] = float(row_as_list[i])
            elif (self.log_parameters_reading_types.get(param) == 'status_parameter_reading'):
                status_parameter_readings[param] = float(row_as_list[i])
            elif (self.log_parameters_reading_types.get(param) == 'profile_reading'):
                profile_reading[param] = float(row_as_list[i])

        utc_dt = raw_tm.convert_time(row_time_ids)

        return {
                'timestamp' : utc_dt,
                'parameter_readings' : parameter_readings,
                'status_parameter_readings' : status_parameter_readings,
                'profile_reading' : profile_reading
        }

    def process_data(self):
        last_line_num_fixed = self.log_file_line_num - 1
        parameter_readings_dictlist = defaultdict(list)
        status_parameter_readings_dictlist = defaultdict(list)
        profile_readings_dictlist = defaultdict(list)
        temp_params_dict = defaultdict(list)
        num_new_readings = 0
        raw_time_manager = timemanager.RawTimeManager(self.log_time_zone)

        for line_number, line in enumerate(self.log_data):
            if (last_line_num_fixed <= line_number):
                readings_map = self.process_row(line, raw_time_manager)
                timestamp = readings_map.get('timestamp')
                parameter_readings = readings_map.get('parameter_readings')
                status_parameter_readings = readings_map.get('status_parameter_readings')
                profile_reading = readings_map.get('profile_reading')
                if parameter_readings:
                    for param_name, param_value in parameter_readings.items():
                        parameter_readings_dictlist[param_name].append({
                            'time' : timestamp,
                            'value' : param_value
                        })
                if status_parameter_readings:
                    for param_name, param_value in status_parameter_readings.items():
                        status_parameter_readings_dictlist[param_name].append({
                            'time' : timestamp,
                            'value' : param_value
                        })
                if profile_reading:
                    for profile_param_name, profile_param_value in profile_reading.items():
                        profile_readings_dictlist[]


def process_campbell_legacy_file(log_id, log_name, file_path, time_zone, time_ids, parameters, reading_types,
    last_line_num=1, load_data=None):

    def _split_current_line(_log_id, current_line, tm, time_params):
        """ Helper function to break current row to each corresponding parameter file.
            Args: current_line (string): The row to process.
        """
        current_line_as_list = current_line.strip().split(',')

        utc_dt = tm.campbell_legacy_time_to_timestamp(current_line_as_list, time_ids)
        indexes = []
        for i, time_id in enumerate(time_params):
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
    last_line_num_fixed = last_line_num - 1
    readings_params_dict = defaultdict(list)
    temp_params_dict = defaultdict(list)
    num_new_readings = 0
    raw_time_manager = timemanager.RawTimeManager(time_zone)

    if load_data:
        for line_number, line in enumerate(load_data):
            _split_current_line(log_id, line, raw_time_manager, time_ids)
    else:
        with open(file_path) as f_in:
            f_list = [line.rstrip('\n') for line in f_in]
        for line_number, line in enumerate(f_list):
            if (last_line_num_fixed < line_number):
                _split_current_line(log_id, line, raw_time_manager, time_ids)

    for parameter, readings_list in readings_params_dict.items():
        target_parameter_file = os.path.join(
            os.path.abspath(folder_path),
            str(log_id),
            log_name,
            'parameters level 0',
            parameter + file_ext
        )
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

    print('Finished splitting file {0}.'.format(file))
    for parameter, readings_list in temp_params_dict.items():
        sorted(readings_list, key=itemgetter(1)) #: Sort by second element, i.e. log_id.
    return num_new_readings, temp_params_dict

def identify_time_ids(time_id_reading_types):
    campbell_legacy = []
    timestamp_format = []
    for name, type in time_id_reading_types.items():
        if type.startswith('int_'):
            campbell_legacy.append(type)
        elif type.startswith('timestamp_'):
            timestamp_format.append((type))
        else:
            return '', -1
    if (len(campbell_legacy) == len(time_id_reading_types)):
        return 'Campbell-Legacy', 0
    elif (len(timestamp_format) == len(time_id_reading_types)):
        return 'Timestamp', 0
    else:
        return '', -1

def run_log_update(log_id, update_info):
    log_name = update_info.get('log_name')
    log_file_path = update_info.get('log_file_path')
    log_file_line_num = update_info.get('log_file_line_num')
    log_time_ids = update_info.get('log_time_ids')
    logger_time_ids = update_info.get('logger_time_ids')
    logger_time_id_types = update_info.get('logger_time_id_types')
    log_time_zone = update_info.get('log_time_zone')
    log_parameters = update_info.get('log_parameters')
    log_reading_types = update_info.get('log_parameters_reading_types')

    time_format, success = identify_time_ids(logger_time_id_types)
    if success == 0:
        if (time_format == 'Campbell-Legacy'):
            num_of_new_readings = 0
            new_rows_dict = defaultdict(list)
            if log_file_line_num == 1:   #: Split whole file.
                with open(log_file_path) as f_in:
                    load_data = [line.rstrip('\n') for line in f_in]    #: Read whole file into memory.
                    num_of_new_readings, new_rows_dict = process_campbell_legacy_file(
                        log_id, log_name, log_file_path, log_time_zone,
                        log_time_ids, log_parameters, log_reading_types, log_file_line_num, load_data
                    )
            else:
                load_data = None
                num_of_new_readings, new_rows_dict = process_campbell_legacy_file(
                    log_id, log_name, log_file_path, log_time_zone, log_time_ids,
                    log_parameters, log_reading_types, log_file_line_num, load_data
                )
            print('Updated parameter files with %s new sites.' % num_of_new_readings)
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

def validate_log_file_info(file_path, line_num):
    if (not file_path or not line_num or line_num < 1):
        return False
    return True

def validate_log_time_info(log_time_ids, log_time_zone, logger_time_ids, logger_time_id_types):
    if (log_time_ids and log_time_zone and logger_time_ids and logger_time_id_types):
        if (logger_time_ids and logger_time_id_types is not None) and \
                (len(logger_time_ids) == len(logger_time_id_types)):
            return True
    return False

def validate_log_parameters(log_parameters, log_parameters_reading_types):
    if (log_parameters and log_parameters_reading_types is not None) and\
            (len(log_parameters) == len(log_parameters_reading_types)):
        for param in log_parameters:
            if param not in log_parameters_reading_types:
                return False
        for key in log_parameters_reading_types.keys():
            if key not in log_parameters:
                return False
        return True
    return False

def prepare_log_update(log_id):
    log_info_data = Log_info_by_log.get_log(log_id)
    log_file_info_data = Log_file_info_by_log.get_log_file_info(log_id)
    log_time_info_data = Log_time_info_by_log.get_log_time_info(log_id)
    log_parameters_info_data = Log_parameters_by_log.get_log_parameters(log_id)
    if log_info_data:
        log_info_map = log_info_data[0]
        log_name = log_info_map.get('log_name')
        if log_file_info_data:
            log_file_info_map = log_file_info_data[0]
            log_file_path = log_file_info_map.get('log_file_path')
            log_last_line_num = log_file_info_map.get('log_file_line_num')
            if not validate_log_file_info(log_file_path, log_last_line_num):
                print("log file validation falied!")
                return -1, None
            if log_time_info_data:
                log_time_info_map = log_time_info_data[0]
                log_time_formats = log_time_info_map.get('log_time_formats')
                log_time_zone = log_time_info_map.get('log_time_zone')
                if logger_time_format_data:
                    logger_time_format_map = logger_time_format_data[0]
                    logger_time_ids = logger_time_format_map.get('logger_time_ids')
                    logger_time_id_types = logger_time_format_data.get('logger_time_id_types')
                    if not validate_log_time_info(log_time_ids, log_time_zone, logger_time_ids, logger_time_id_types):
                        print("log time info validation falied!")
                        return -1, None
                    if log_parameters_info_data:
                        log_parameters_info_map = log_parameters_info_data[0]
                        log_parameters = log_parameters_info_map.get('log_parameters')
                        log_parameters_reading_types = log_parameters_info_map.get('log_reading_types')
                        if not validate_log_parameters(log_parameters, log_parameters_reading_types):
                            print("log parameters validation falied!")
                            return -1, None
                        update_info = {
                            'log_name' : log_name,
                            'log_file_path' : log_file_path,
                            'log_file_line_num' : log_last_line_num,
                            'log_time_ids' : log_time_ids,
                            'log_time_zone' : log_time_zone,
                            'logger_time_ids' : logger_time_ids,
                            'logger_time_id_types' : logger_time_id_types,
                            'log_parameters' : log_parameters,
                            'log_parameters_reading_types' : log_parameters_reading_types
                        }
                        return 0, update_info

def cron_job():
    all_sites_data = Sites.get_all_sites()
    for site in all_sites_data:
        site_id = site.get('site_id')
        all_site_locations = Locations_by_site.get_all_locations(site_id)
        for location in all_site_locations:
            location_id = location.get('location_id')
            all_location_logs = Logs_by_location.get_all_logs(location_id)
            for log in all_location_logs:
                log_id = log.get('log_id')
                log_update_info_data = Log_update_schedule_by_log.get_log_updates(log_id)
                if log_update_info_data:
                    log_update_info_map = log_update_info_data[0]
                    log_update_interval_map = log_update_info_map.get('log_update_interval')
                    log_update_interval_id = log_update_interval_map.get('log_update_interval_id')
                    log_update_interval = log_update_interval_map.get('log_update_interval')
                    log_next_update = log_update_info_map.get('log_next_update')
                    if log_next_update and \
                        (log_next_update <= datetime.utcnow()):
                            success, update_info = prepare_log_update(log_id)
                            if (success == 0 and update_info):
                                upd = UpdateLog(**update_info)

                                #run_log_update(log_id, update_info)
                                if (log_update_interval_id == 'daily'):
                                    log_last_update = log_next_update
                                    log_next_update += timedelta(days=1)
                                elif (log_update_interval_id == 'hourly'):
                                    log_last_update = log_next_update
                                    log_next_update += timedelta(hours=1)
                                Log_update_schedule_by_log(log_id=log_id).update(
                                    log_last_update=log_last_update,
                                    log_next_update=log_next_update
                                )
