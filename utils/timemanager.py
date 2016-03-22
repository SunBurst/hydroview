import calendar
import time

import pytz

from collections import OrderedDict
from datetime import datetime
from pytz import timezone

from settings.base import TIME_ZONE

TIME_FORMATS = OrderedDict([
    ('%a', "(%a) Locale’s abbreviated weekday name."),
    ('%A', "(%A) Locale’s full weekday name."),
    ('%b', "(%b) Locale’s abbreviated month name."),
    ('%B', "(%B) Locale’s full month name."),
    ('%c', "(%c) Locale’s appropriate date and time representation."),
    ('%d', "(%d) Day of the month as a decimal number [01,31]."),
    ('%H', "(%H) Hour (24-hour clock) as a decimal number [00,23]."),
    ('%I', "(%I) Hour (12-hour clock) as a decimal number [01,12]."),
    ('%j', "(%j) Day of the year as a decimal number [001,366]."),
    ('%m', "(%m) Month as a decimal number [01,12]."),
    ('%M', "(%M) Minute as a decimal number [00,59]."),
    ('%p', "(%p) Locale’s equivalent of either AM or PM. (1)"),
    ('%S', "(%S) Second as a decimal number [00,61]. (2)"),
    ('%U', "(%U) Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0. (3)"),
    ('%w', "(%w) Weekday as a decimal number [0(Sunday),6]."),
    ('%W', "(%W) Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0. (3)"),
    ('%x', "(%x) Locale’s appropriate date representation."),
    ('%X', "(%X) Locale’s appropriate time representation."),
    ('%y', "(%y) Year without century as a decimal number [00,99]."),
    ('%Y', "(%Y) Year with century as a decimal number."),
    ('%z', "(%z) Time zone offset indicating a positive or negative time difference from UTC/GMT of the form +HHMM or -HHMM, where H represents decimal hour digits and M represents decimal minute digits [-23:59, +23:59]."),
    ('%Z', "(%Z) Time zone name (no characters if no time zone exists)."),
    ('hourminute', "(HourMinute) Hour and minute (24-hour clock) combined as a decimal number")
])

CUSTOM_TIME_FORMATS = OrderedDict([
    ('hourminute', "(HourMinute) Hour and minute (24-hour clock) combined as a decimal number")
])

class RawTimeManager(object):

    def __init__(self, time_zone):
        self.raw_data_tz = timezone(time_zone)

    def convert_time(self, time_ids):
        for key, val in time_ids.items():
            print(key, type(key))
            if key not in TIME_FORMATS and key not in CUSTOM_TIME_FORMATS:
                print("Time format not supported!")
            elif key in CUSTOM_TIME_FORMATS:     #: Call your custom time format parser here.
                if key == 'hourminute':
                    time_fmt_fixed, time_string_fixed = self.parse_hourminute(val)
                    del time_ids[key]
                    time_ids[time_fmt_fixed] = time_string_fixed    #: Replace with "%H:%M" : "HH:MM".
                # if key == ...... #: Call your custom time format parser here.

        time_id_str = ",".join(time_ids.values())
        time_id_fmt = ",".join(time_ids.keys())
        t = time.strptime(time_id_str, time_id_fmt)
        dt = datetime.fromtimestamp(time.mktime(t))
        loc_dt = self.raw_data_tz.localize(dt)
        utc_dt = loc_dt.astimezone(pytz.utc)
        return utc_dt

    def parse_hourminute(self, hm):
        hm_int = int(hm)
        hour = int(hm_int/100)
        temp_min_hour = hm
        parsed_fmt = "%H:%M"
        parsed_time = ""

        if (len(temp_min_hour) == 1):            #: 0
            hour = 0
            minute = temp_min_hour
            parsed_time = "00:0" + minute
        elif (len(temp_min_hour) == 2):           #: 10 - 50
            hour = 0
            minute = temp_min_hour[-2:]
            parsed_time = "00:" + minute
        elif (len(temp_min_hour) == 3):          #: 100 - 950
            hour = temp_min_hour[:1]
            minute = temp_min_hour[-2:]
            parsed_time = "0" + hour + ":" + minute
        elif (len(temp_min_hour) == 4):          #: 1000 - 2350
            hour = temp_min_hour[:2]
            minute = temp_min_hour[-2:]
            parsed_time = hour + ":" + minute

        return parsed_fmt, parsed_time

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


