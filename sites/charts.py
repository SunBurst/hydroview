import utils.timemanager as timemanager

from .sites import SiteData
from .models import Parameters_by_sensor

class ChartData(object):

    @classmethod
    def get_humidity_data_by_day(cls, days):#, user):
        tm = timemanager.TimeManager()
        series_data = []
        #sites = SiteData.get_all_sites()
        #data = {'location' : [], 'time': [], 'value': [],
        #    }

        rows = Parameters_by_sensor.objects.filter(sensor='Daily', parameter = 'humidity', qc_level=0).limit(days)
        location_data = {"name" : 'Malma Island Level 0', "data" : []}

        for row in rows:
            time_ts_millis = tm.utc_dt_to_utc_ts_millis(row.time)
            value = row.value
            location_data["data"].append([time_ts_millis, value])

        series_data.append(location_data)
        return series_data

        #for location in locations:

        #    location_data = {"name" : location, "data" : []}

        #    sensor_name = location + '_diag'
        #    rows = Readings_by_sensor.objects.filter(sensor = sensor_name, parameter = 'battery').limit(days)


        #    for row in rows:
        #        time_ts_millis = tm.utc_dt_to_utc_ts_millis(row.time)

        #        value = row.value

         #       location_data["data"].append([time_ts_millis, value])


            #series_data.append(location_data)

        #return series_data