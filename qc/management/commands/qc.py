import os
import calendar
import datetime
import time
import configparser
import pytz
from pytz import timezone
from collections import defaultdict
from django.core.management.base import BaseCommand
#import utils.dbmanager as db
from utils import timemanager
import qc.management.qc_min_max as qc_min_max
import qc.management.qc_missing_readings as qc_missing_readings
from utils import timemanager
from sites.locations import LocationData
from sites.sensors import SensorData

class Command(BaseCommand):

    #cfg_ids = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, 'cfg', 'identifiers.INI')
    #cfg_qc = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, 'cfg', 'qcinfo.INI')
    #cfg_ids = ('cfg/identifiers.INI')
    #cfg_qc = ('cfg/qcinfo.INI')
    #config_parser_ids = configparser.ConfigParser()
    #config_parser_ids.read(cfg_ids)
    #config_parser_qc = configparser.ConfigParser()
    #config_parser_qc.read(cfg_qc)

    def run_qc(self, from_ts_utc, to_ts_utc):
        """ Perform quality control (min-max & missing sites) on the specified timerange.
        Args:
            from_ts_utc (int): Quality control from this timestamp onwards (including given timestamp).
            to_ts_utc (int): Quality control up to this timestamp.
        Returns:
            1 if QC succeeded
            0 if QC failed
        """
        try:
            locations = LocationData.get_site_locations('Erken')
        except: 
            print("Locations query failed!")
            return

        for location in locations:
            location_name = location.get('location')
            sensor_names = SensorData.get_sensors_by_location(location_name)
            
            for sensor in sensor_names:
                sensor_name = sensor.get('sensor')
                params = SensorData.get_sensor(sensor_name)
                
                qc_min_max.qc_min_max_on_sensor(from_ts_utc, to_ts_utc, sensor_name)

                for param in params:
                    print("QC missing sites on parameter " + param + " with sensor name = " + sensor_name)
                    #if (param == 'air_temp_2' and sensor_name == 'island_daily'):
                    qc_missing_readings.find_missing_readings_by_time(param, sensor_name, from_ts_utc, to_ts_utc)
                    #temp_query_params = [sensor_name, param, from_ts_utc, to_ts_utc]
                    #query_missing_params.append(temp_query_params)
                #print("SENSOR " + sensor_name) 
                #print("MIN MAX", query_min_max_params)
                #print("MISSING PARAMS ", query_missing_params)
            
            
                #if query_missing_params:
                #    find_missing_readings_by_time(query_missing_params, sensor_name, from_ts_utc, to_ts_utc)
				
                #db.cluster_disconnect()
        return

    

		#success_flag = run_full_qc(from_ts_utc, to_ts_utc)

		
    #def qc_on_timerange(from_datetime=None, to_datetime=None):
    def handle(self, *args, **timerange):
        """ Convert given time interval to utc.  If no starting time is given, fetch fallback value located in
            the qcinfo configuration file.  If no such value exists, abort operation and encourage the user to
	        set it.  If no ending time is provided, get the current time.  Once set up, pass the time intervals. 
        Args:
            from_datetime (datetime): Run quality control from this time onwards
            to_datetime (datetime): Run quality control up to this time
        Returns:
            0 if no fallback value is found in configuration file.
            1 if quality control succeeded.
	    """
        
        tm = timemanager.TimeManager()
        
        from_dt = timerange.get('from_datetime')
        to_dt = timerange.get('to_datetime')
        #from_dt = from_datetime
        #to_dt = to_datetime
        if from_dt:
            from_dt_utc = tm.local_dt_to_utc_dt(from_dt)
        else: 
            #from_dt = tm.get_dt_fallback_value()
            if not from_dt:
                msg = 'No starting date detected! Please provide the first date to quality control in file "%s"' % cfg_qc 
                msg += "using the format YYYY-MM-DD HH-MM-SS in local time.\n")
                print(msg)
                return
            #from_dt = tm.dt_str_to_datetime(from_dt_str)
            from_dt_utc = tm.local_dt_to_utc_dt(from_dt)
        if to_dt:
            to_dt_utc = tm.local_dt_to_utc_dt(to_dt)
        else:
            to_dt = tm.get_current_datetime()
            to_dt_utc = tm.local_dt_to_utc_dt(to_dt)
        #split_queries(from_dt_utc, to_dt_utc, days_limit_per_query)
        (from_ts_utc, to_ts_utc) = tm.datetime_to_timestamp(from_dt_utc, to_dt_utc)
        print("Performing quality control on time interval %s to %s" % (from_dt, to_dt))
        self.run_qc(from_ts_utc, to_ts_utc)
        #db.cluster_disconnect()

        #if(success(success_flag)):
        #    return 1
        #else:
        #    return 0

#if __name__=='__main__':
#    test1 = datetime.datetime(2014,1,1,0,0,0)
#    test2 = datetime.datetime(2015,1,1,0,0,0)
#    success = qc_on_timerange(test1,test2)
    
	#new_test(test1,test2)
    #print(success)

    #run_full_qc([1396303200000,1398895200000])
    #run_qc()
    #run_qc_min_max('humidity','island_daily',[-10.0,1000.0])
    #qc_min_max('humidity','island_daily',[-10.0,1000.0],[1399248000000,1401926400000])
    #qc_min_max('humidity','island_daily',[-10.0,1000.0],[None,1402005600000])
    #qc_min_max('humidity','island_daily',[-10.0,1000.0],[1402005600000,1402005600000])
    #qc_min_max('humidity','island_daily',[-10.0,1000.0],[1402005600000,None])
    #qc_min_max('humidity','island_daily',[-10.0,1000.0])