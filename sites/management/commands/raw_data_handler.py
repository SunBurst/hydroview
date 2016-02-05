__author__ = 'Marcus'

import calendar
import datetime
import os
#import pytz
import time
import configparser
#import timezone
from collections import defaultdict
from operator import itemgetter
#from pytz import timezone
from utils import timemanager

""" Script consisting of a bunch of function to help formatting raw file structures """

cfg = ('cfg/identifiers.INI')
#cfg = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, 'cfg', 'identifiers.INI')

config_parser = configparser.ConfigParser()
config_parser.read(cfg)

tm = timemanager.TimeManager()
#local_tz = timezone('Europe/Stockholm') #
#fmt = '%Y-%m-%d %H:%M:%S %Z%z' #

def identify_sensor_id(row):

    """ Identifies the sensor id of the given row. 
    Args: 
        row (list): reading to identify.
    Returns:
        The sensor id of the given row.
		
    """
    return row[0]			

def split_file(path_to_file, most_recent_line_num=None, load_data=None):
    """ 
    """

    def _split_current_line(current_line):
        """ Helper function to break current row to each corresponding parameter file.
            Args: current_line (string): The row to process. 
        """
        current_line_as_list = current_line.strip().split(',')
        sensor_id = identify_sensor_id(current_line_as_list)

        sensor_name = config_parser.get('SENSOR_IDS', sensor_id)	
        raw_file_params_order_list = config_parser.get('RAW_FILE_ORDERS', sensor_name).split(',')
        time_identifiers_list = config_parser.get('TIME_IDENTIFIERS', sensor_name).split(',')		#: Year, julianday, hour (minute)

        #ts = tm.raw_format_to_timestamp(current_line_as_list, time_identifiers_list)    #: WORKS FOR RAW QUERIES
        #ts_as_string = str(ts)    #: WORKS FOR RAW QUERIES
        utc_dt = tm.raw_format_to_timestamp(current_line_as_list, time_identifiers_list)
        indexes = []														#: Replace raw time identifiers with timestamp representation.
        for count,ids in enumerate(time_identifiers_list):
            indexes.append(count+1)

        for index in sorted(indexes, reverse = True):
            del current_line_as_list[index]

        del current_line_as_list[0]

        for parameter, val in zip(raw_file_params_order_list, current_line_as_list):
            #val_as_string = str(val)    #: WORKS FOR RAW QUERIES
            #values = ','.join([sensor_name, parameter, ts_as_string, val_as_string])		#: WORKS FOR RAW QUERIES
            val_float = float(val)
            values = [sensor_name, parameter, utc_dt, val_float]
            readings_params_dict[parameter].append(values)


    folder_path,file = os.path.split(os.path.abspath(path_to_file))
    file_ext = os.path.splitext(os.path.abspath(path_to_file))[1]
    
    readings_params_dict = defaultdict(list)
    temp_params_dict = defaultdict(list)
    num_new_readings = 0

    if load_data:
        for line_number, line in enumerate(load_data):
            _split_current_line(line)
    else:
        with open(path_to_file) as f_in:
            f_list = [line.rstrip('\n') for line in f_in]
        for line_number, line in enumerate(f_list):
            if (most_recent_line_num < line_number):
                _split_current_line(line)

    for parameter, readings_list in readings_params_dict.items():
        target_parameter_file = os.path.join(os.path.abspath(folder_path), 'parameters', parameter + file_ext)
        os.makedirs(os.path.dirname(target_parameter_file), exist_ok=True)
	
        with open(target_parameter_file, 'a+') as f_out:
            for row in readings_list:    
                num_new_readings += 1
                temp_params_dict[parameter].append(row)
                #temp_params_dict[parameter].append(row.split(',')) 
                f_out.write("%s\n" % (row))
		
    print('Finished splitting file "%s".' % file)
    print("Sorting sites in order to optimize database insertion..")
    for parameter, readings_list in temp_params_dict.items():
        sorted(readings_list, key=itemgetter(1)) #: Sort by second element, i.e. sensor id.
    return num_new_readings,temp_params_dict

def fix_floating_points(location, path_to_file, most_recent_line_num=None):

    """ Replaces . with .0 and -. with -.0 since the underlying Cassandra database only accept floating points
            leading with zeros.
        Args: location (string): the location of interest
              path_to_file (string): source file input
              most_recent_line_num (int): If None, process whole file.  
                                 If an integer, process from this line number until EOF.
        Returns:
            fixed_file (string): The absolute path to the new fixed file.
            updated_most_recent_line_num (int): Source file has floating points fixed up to this line number.
    """
	
    folder_path, infile = os.path.split(os.path.abspath(path_to_file))
    file_name, file_ext = os.path.splitext(infile)
    fixed_file = os.path.join(os.path.abspath(folder_path), location, file_name + "_fixed" + file_ext)
    os.makedirs(os.path.dirname(fixed_file), exist_ok=True)

    #f_in =  open(path_to_file)
    f_out = open(fixed_file, 'a')
    with open (path_to_file) as f_in:
        f_list = [line.rstrip('\n') for line in f_in]
	
    replacements = {',.':',0.',',-.':',-0.'}
    updated_most_recent_line_num = most_recent_line_num

    if not most_recent_line_num:
        for line_number, line in enumerate(f_list):
            if (line_number < len(f_list)-1):
                for src, target in replacements.items():
                    line = line.replace(src, target)
                    f_list[line_number] = line
                f_out.write("%s\n" %(line))
            else:
                updated_most_recent_line_num = line_number    #: Store last line
                for src, target in replacements.items():
                    line = line.replace(src, target)
                    f_list[line_number] = line
                f_out.write("%s\n" %(line))

    else:			
        for line_number, line in enumerate(f_list):
            if (most_recent_line_num < line_number): #: Update!
                updated_most_recent_line_num = line_number
                for src, target in replacements.items():
                    line = line.replace(src, target)
                    f_list[line_number] = line
                f_out.write("%s\n" %(line))
	#f_in.close()
    f_out.close()
    print('Fixed floating points in file "%s"' % infile)
    print('Floating points fixed up to line number %s' % (updated_most_recent_line_num+1))   #: An offset of one since notepads etc are counting from line number one instead of zero.
    return fixed_file, updated_most_recent_line_num

def lines_to_split(path_to_file, most_recent_line_num=None):
    """ Reads the whole file of interest into memory and passes it on for file splitting.
    Args:
        path_to_file (string): the absolute path to file
        most_recent_line_num (int): If None, read whole file.  If an integer, just pass.
    Returns:
        num_new_readings (int): The total number of new sites.
        readings_dict (defaultdict(list)): Dictionary with keys representing each parameter where its 
            corresponding value contains a list of sites.
    """
    if not most_recent_line_num:   #: Split whole file.
        with open(path_to_file) as f_in:
            f_list = [line.rstrip('\n') for line in f_in]    #: Read whole file into memory. 
            num_new_readings, readings_dict = split_file(path_to_file, most_recent_line_num, f_list)

    else:
        load_data = None
        num_new_readings, readings_dict = split_file(path_to_file, most_recent_line_num, load_data)

    return num_new_readings, readings_dict

def start_file_watch(location, updated_most_recent_line_num):
    print("Updating configuration file.")
    updated_line_num = str(updated_most_recent_line_num)
    config_parser.set('RECENT_READINGS', location, updated_line_num)

    with open(cfg, 'w') as temp_write_cfg:
        config_parser.write(temp_write_cfg)

def update_files(location, path_to_file, watch_file=True):
    """ Performs a full update of the raw files including fixing floating points, 
        splitting source file into parameter files and start file watching.
    Args: 
        location (string): the location of interest
        path_to_file (string): source file input
        watch_file (boolean): If True, starting watching this file by storing and 
            updating latest line number processed in the identifiers.INI file.  If False, process file 
            without storing this tracking information.
    Returns:
        num_new_readings (int): The total number of new sites found in file.
        readings_dict (defaultdict(list)): Dictionary with keys representing each parameter where its 
            corresponding value contains a list of sites.
    """

    location_most_recent_line_num = location + "_most_recent_line_num"
    most_recent_line_num = config_parser.get('RECENT_READINGS', location_most_recent_line_num)
    
    if most_recent_line_num:
        most_recent_line_num = int(most_recent_line_num)
    new_filepath, updated_most_recent_line_num = fix_floating_points(location, path_to_file, most_recent_line_num)
    
    if (isinstance(updated_most_recent_line_num, int)):
        if(most_recent_line_num != updated_most_recent_line_num):
            print("New sites detected! Beginning file splitting..")
            num_new_readings, readings_dict = lines_to_split(new_filepath, most_recent_line_num)
            print('Updated parameter files with %s new sites.' % num_new_readings)
            if watch_file:
                start_file_watch(location_most_recent_line_num, updated_most_recent_line_num)
            return num_new_readings, readings_dict
        else:
            print("No new sites detected.")
            return 0, {}
    print("File updating done!")

#if __name__=='__main__':
#    user_input_location = input("Enter name of location (e.g. island) to fix: ")
#    user_input_file = input("Enter full path to file to process: ")
#    assert os.path.exists(user_input_file), "File not found at, "+str(user_input_file)
#    while True:
#        user_input_watch = input("Start watching this file? (y/n): ")
#        if user_input_watch in ['y', 'n']:
#            break
#        else:
#            print('That is not a valid option!')
#    if user_input_watch == 'y':
#        num_readings, sites = update_files(user_input_location, user_input_file, watch_file=True)
#    else:
#        num_readings, sites = update_files(user_input_location, user_input_file, watch_file=False)
    