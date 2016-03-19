import calendar
import datetime
import pytz
from pytz import timezone

from settings.base import TIME_ZONE

class RawTimeManager(object):

    def __init__(self, time_zone):
        self.raw_data_tz = timezone(time_zone)

    def campbell_legacy_time_to_timestamp(self, line_as_list, time_ids):
        """
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

        if (len(time_ids) == 2):
            year = int(line_as_list[1])
            julianday = int(line_as_list[2])-1

        elif (len(time_ids) == 3):
            year = int(line_as_list[1])
            julianday = int(line_as_list[2])-1
            hour = int(line_as_list[3])
            hour = int(hour/100)
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

        return utc_dt

class TimeManager(object):

    def __init__(self):
        self.local_tz = timezone(TIME_ZONE)

    def datetime_to_timestamp(self, from_datetime_utc, to_datetime_utc):
        from_ts_utc = self.utc_dt_to_utc_ts_millis(from_datetime_utc)
        to_ts_utc = self.utc_dt_to_utc_ts_millis(to_datetime_utc)
        return (from_ts_utc, to_ts_utc)

    def dt_str_to_datetime(self, dt_str):
        return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

    def local_dt_to_utc_dt(self, local_dt):
        loc_dt = self.local_tz.localize(local_dt)
        utc_dt = loc_dt.astimezone(pytz.utc)
        return utc_dt

    def utc_dt_to_local_dt(self, utc_dt):
        utc = pytz.utc
        loc_dt = utc.localize(utc_dt).astimezone(self.local_tz)
        return loc_dt

    def utc_dt_to_utc_dt_tz(self, utc_dt):
        utc = pytz.utc
        utc_dt_tz = utc.localize(utc_dt)
        return utc_dt_tz

    def timestamp_to_datetime_utc(self, ts):
        return datetime.datetime.utcfromtimestamp(ts)

    def utc_dt_to_utc_ts_millis(self, utc_dt):
        utc_ts = int(calendar.timegm(utc_dt.timetuple()))
        utc_ts_millis = utc_ts*1000
        return utc_ts_millis

    def json_date_handler(self, dt):
        """JSON serializer for datetime objects not serializable by default json code. """
        return dt.isoformat() if hasattr(dt, 'isoformat') else dt


