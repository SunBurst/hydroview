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
from readings.models import Parameters_readings_by_log, Profiles_readings_by_log, Status_parameter_readings_by_log
from sites.models import Sites
from utils import logging, parser, timemanager

db_settings = parser.DatabaseSettingsParser('cassandra_config.ini')
db_settings.load_local_settings()

connection.setup([db_settings.cassandra_host], db_settings.cassandra_keyspace)
logging.setup_logging()

class UpdateLog(object):

    def __init__(self, log_id, **kwargs):
        self.log_id = log_id
        self.log_name = kwargs.get('log_name')
        self.default_raw_qc_level = 0
        self.log_file_path = kwargs.get('log_file_path')
        self.log_file_line_num = kwargs.get('log_file_line_num')
        self.log_time_zone = kwargs.get('log_time_zone')
        self.log_time_formats = kwargs.get('log_time_formats')
        self.log_parameters = kwargs.get('log_parameters')
        self.log_parameters_reading_types = kwargs.get('log_parameters_reading_types')

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
                time_id_fmt = self.log_time_formats.get(param)
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

    def process_data(self, data):
        last_line_num_fixed = self.log_file_line_num - 1
        parameter_readings_dictlist = defaultdict(list)
        status_parameter_readings_dictlist = defaultdict(list)
        profile_readings_dictlist = defaultdict(list)
        raw_time_manager = timemanager.RawTimeManager(self.log_time_zone)
        num_of_lines_processed = 0
        for line_number, line in enumerate(data):

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
                    profile_readings_dictlist[self.log_name].append({
                        'time' : timestamp,
                        'profile_reading' : profile_reading
                    })
                num_of_lines_processed += 1

        updated_log_file_line_num = self.log_file_line_num + num_of_lines_processed

        return {
            'parameter_readings' : parameter_readings_dictlist,
            'status_parameter_readings' : status_parameter_readings_dictlist,
            'profile_readings' : profile_readings_dictlist,
            'update_log_line_num' : updated_log_file_line_num
        }

    def store_parameter_readings(self, readings):

        for param_name, readings_list in readings.items():
            for reading in readings_list:
                timestamp = reading.get('time')
                value = reading.get('value')

                Parameters_readings_by_log.create(
                    log_id=self.log_id,
                    reading_parameter=param_name,
                    reading_qc_level=self.default_raw_qc_level,
                    reading_time=timestamp,
                    reading_value=value
                )

    def store_status_parameter_readings(self, readings):

        for param_name, readings_list in readings.items():
            for reading in readings_list:
                timestamp = reading.get('time')
                value = reading.get('value')

                Status_parameter_readings_by_log.create(
                    log_id=self.log_id,
                    reading_parameter=param_name,
                    reading_qc_level=self.default_raw_qc_level,
                    reading_time=timestamp,
                    reading_value=value
                )

    def store_profile_readings(self, readings):

        for profile_name, readings_list in readings.items():
            for profile in readings_list:
                timestamp = profile.get('time')
                profile_reading = profile.get('profile_reading')
                Profiles_readings_by_log.create(
                    log_id=self.log_id,
                    reading_qc_level=self.default_raw_qc_level,
                    reading_profile=profile_name,
                    reading_time=timestamp,
                    reading_values=profile_reading
                )

    def update_log_line_num(self, new_line_num):

        Log_file_info_by_log(log_id=self.log_id).update(log_file_line_num=new_line_num)

    def update_log_update_info(self, log_update_time):

        Log_update_schedule_by_log(log_id=self.log_id).update(
            log_update_is_active=True,
            log_last_update=log_update_time,
        )

        #self.new_data.get('status_parameter_readings')
        #self.new_data.get('profile_readings')


    #folder_path, file = os.path.split(os.path.abspath(file_path))
    #file_ext = os.path.splitext(os.path.abspath(file_path))[1]  #: e.g. .dat
    #last_line_num_fixed = last_line_num - 1
    #readings_params_dict = defaultdict(list)
    #temp_params_dict = defaultdict(list)
    #num_new_readings = 0
    #raw_time_manager = timemanager.RawTimeManager(time_zone)

    #if load_data:
    #    for line_number, line in enumerate(load_data):
    #        _split_current_line(log_id, line, raw_time_manager, time_ids)
    #else:
    #    with open(file_path) as f_in:
    #        f_list = [line.rstrip('\n') for line in f_in]
    #    for line_number, line in enumerate(f_list):
    #        if (last_line_num_fixed < line_number):
    #            _split_current_line(log_id, line, raw_time_manager, time_ids)

    #for parameter, readings_list in readings_params_dict.items():
    #    target_parameter_file = os.path.join(
    #        os.path.abspath(folder_path),
    #        str(log_id),
    #        log_name,
    #        'parameters level 0',
    #        parameter + file_ext
    #    )
    #    os.makedirs(os.path.dirname(target_parameter_file), exist_ok=True)

    #    with open(target_parameter_file, 'a+') as f_out:
    #        for row in readings_list:
    #            num_new_readings += 1
    #            temp_params_dict[parameter].append(row)
    #            log_id = row[0]
    #            param_name = row[1]
    #            qc_level = row[2]
    #            time_str = str(row[3])
    #            value = row[4]
    #            f_out.write(u"{0} {1} {2} {3} {4}\n".format(
    #                log_id,
    #                param_name,
    #                qc_level,
    #                time_str,
    #                value
    #            ))

    #print('Finished splitting file {0}.'.format(file))
    #for parameter, readings_list in temp_params_dict.items():
    #    sorted(readings_list, key=itemgetter(1)) #: Sort by second element, i.e. log_id.
    #return num_new_readings, temp_params_dict

def validate_log_file_info(file_path, line_num):
    if (not file_path or not line_num or line_num < 1):
        return False
    return True

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
                        'log_time_formats' : log_time_formats,
                        'log_time_zone' : log_time_zone,
                        'log_parameters' : log_parameters,
                        'log_parameters_reading_types' : log_parameters_reading_types
                    }
                    return 0, update_info

def run_update_cron_job():
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
                    log_update_is_active = log_update_info_map.get('log_update_is_active')
                    if log_update_is_active:
                        success, update_info = prepare_log_update(log_id)
                        if (success == 0 and update_info):
                            upd = UpdateLog(log_id, **update_info)
                            log_data = upd.load_file()
                            readings_map = upd.process_data(log_data)
                            if readings_map.get('parameter_readings'):
                                parameter_readings = readings_map.get('parameter_readings')
                                upd.store_parameter_readings(parameter_readings)
                            if readings_map.get('status_parameter_readings'):
                                status_parameter_readings = readings_map.get('status_parameter_readings')
                                upd.store_status_parameter_readings(status_parameter_readings)
                            if readings_map.get('profile_readings'):
                                profile_readings = readings_map.get('profile_readings')
                                upd.store_profile_readings(profile_readings)
                            update_log_line_num = readings_map.get('update_log_line_num')
                            upd.update_log_line_num(update_log_line_num)
                            log_update_time = datetime.utcnow()
                            upd.update_log_update_info(log_update_time)

