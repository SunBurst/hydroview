import calendar
import configparser
import datetime
import pytz
from pytz import timezone

from settings.settings import TIME_ZONE

class TimeManager(object):

    def __init__(self):
        self.parser_ids = configparser.ConfigParser()
        self.parser_qcinfo = configparser.ConfigParser()
        self.cfg_ids = ('cfg/identifiers.INI')
        self.cfg_qcinfo = ('cfg/qcinfo.INI')
        self.parser_ids.read(self.cfg_ids)
        self.parser_qcinfo.read(self.cfg_qcinfo)
        self.local_tz = timezone(TIME_ZONE)
        #self.local_tz = self.get_local_timezone()
        self.raw_data_tz = self.get_raw_data_timezone()    #: Can be commented out if the sites timezone is identical to the local one.
        #self.raw_data_tz = self.get_local_timezone()    #: Uncomment this and comment out the above if the raw data timezone is identical to the local one.

    def datetime_to_timestamp(self, from_datetime_utc, to_datetime_utc):
        from_ts_utc = self.utc_dt_to_utc_ts_millis(from_datetime_utc)    
        to_ts_utc = self.utc_dt_to_utc_ts_millis(to_datetime_utc)
        return (from_ts_utc, to_ts_utc)

    def dt_str_to_datetime(self, dt_str):
        return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

    def get_current_datetime(self):
        return datetime.datetime.now()

    def get_dt_fallback_value(self):
        str_fallback_from_config = self.parser_qcinfo.get('QC_TIME_INFO', 'datetime_fallback')
        if str_fallback_from_config:
            print('Found fallback datetime "%s" in %s' % (str_fallback_from_config, self.cfg_qcinfo))
            dt_fallback = self.dt_str_to_datetime(str_fallback_from_config)
            return dt_fallback

    #def get_local_timezone(self):
    #    tz_from_config = self.parser_ids.get('LOCAL_INFO', 'local_timezone')
    #    if tz_from_config:
    #        print('Found local timezone "%s" in %s' % (tz_from_config, self.cfg_ids))
    #        local_tz = timezone(tz_from_config)
    #    else:
    #        print('Local timezone not found in configuration file "%s"' % self.cfg_ids)
        
    #    return local_tz

    def get_raw_data_timezone(self):
        tz_from_config = self.parser_ids.get('LOCAL_INFO', 'raw_data_timezone')
        if tz_from_config:
            print('Found raw data timezone "%s" in %s' % (tz_from_config, self.cfg_ids))
            local_tz = timezone(tz_from_config)
        else:
            print('Local timezone not found in configuration file "%s"' % self.cfg_ids)
        
        return local_tz

    def local_dt_to_utc_dt(self, local_dt):
        loc_dt = self.local_tz.localize(local_dt)
        utc_dt = loc_dt.astimezone(pytz.utc)
        return utc_dt
    
    def utc_dt_to_local_dt(self, utc_dt):
        utc = pytz.utc
        loc_dt = utc.localize(utc_dt).astimezone(self.local_tz)
        return loc_dt

    def raw_format_to_timestamp(self, line_as_list, time_indexes):

        """ Helper function for raw_data_handler.py. 
            Converts raw file date and time format to timestamp (millis).
        Args:
            line_as_list (list): Current reading
            time_indexes (list): Determines which parameters that indicate date and time.
        Returns:
            The timestamp based on type of reading.

        """

        year = 0
        julianday = 0
        hour = 0
        minute = 0
        second = 0

        if ("year" in time_indexes):
            year = int(line_as_list[1])
        if ("julianday" in time_indexes):
            julianday = int(line_as_list[2])-1
        if ("hour" in time_indexes):
            hour = int(line_as_list[3])
            hour = int(hour/100)            #: e.g. 2200 -> 22
        if ("hour_minute" in time_indexes):
            temp_min_hour = line_as_list[3]
            if (len(temp_min_hour) == 1):            #: 0
                hour = 0
                minute = int(temp_min_hour)
            elif (len(temp_min_hour) == 2):           #: 10 - 50
                hour = 0
                minute = int(temp_min_hour[-2:])
            elif (len(temp_min_hour) == 3):          #: 100 - 950
                hour = int(temp_min_hour[:1])
                minute = int(temp_min_hour[-2:])
            elif (len(temp_min_hour) == 4):          #: 1000 - 2350
                hour = int(temp_min_hour[:2])
                minute = int(temp_min_hour[-2:])

        date = datetime.datetime

        #: if current year is a leap year, make entry for feb 29th.

        if (calendar.isleap(year) is False):
            date = datetime.datetime(year, 1, 1, hour, minute, second) + datetime.timedelta(julianday)
        else:
            if (julianday == 59):
                date = datetime.datetime(year, 2, 29, hour, minute, second)
            else:
                date = datetime.datetime(year, 1, 1, hour, minute, second) + datetime.timedelta(julianday)

        loc_dt = self.raw_data_tz.localize(date)
        utc_dt = loc_dt.astimezone(pytz.utc)
        #utc_ts_millis = self.utc_dt_to_utc_ts_millis(utc_dt) #: WORKS FOR RAW QUERIES
        #utc_ts = int(calendar.timegm(utc_dt.timetuple()))
        #utc_ts_millis = utc_ts*1000
        #return utc_ts_millis #: WORKS FOR RAW QUERIES
        return utc_dt

    def timestamp_to_datetime_utc(self, ts):
        return datetime.datetime.utcfromtimestamp(ts)

    def utc_dt_to_utc_ts_millis(self, utc_dt):
        utc_ts = int(calendar.timegm(utc_dt.timetuple()))
        utc_ts_millis = utc_ts*1000
        return utc_ts_millis