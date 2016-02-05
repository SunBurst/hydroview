import utils.timemanager as timemanager
#from .models import Locations, Sensors_by_location, Readings_by_sensor, Sensor_status_by_location

class ChartData(object):

    @classmethod
    def get_status_data_by_day(cls, days):#, user):
        tm = timemanager.TimeManager()
        series_data = []
        locations = [location.name for location in Locations.objects.filter(bucket=0)]
        #data = {'location' : [], 'time': [], 'value': [],
        #    }

        for location in locations:
            #location_series = {}
            location_data = {"name" : location, "data" : []}
            #location_data = []
            sensor_name = location + '_diag'
            rows = Readings_by_sensor.objects.filter(sensor = sensor_name, parameter = 'battery').limit(days)
            #location_series['name'] = location

            for row in rows:
                time_ts_millis = tm.utc_dt_to_utc_ts_millis(row.time)
               # data['time'].append(time_ts_millis)
               # data['value'].append(row.value)
                value = row.value
                #location_data['time'].append(time_ts_millis)
                #location_data['values'].append(value)
                location_data["data"].append([time_ts_millis, value])
                #location_series['data'] = location_data

            series_data.append(location_data)

        return series_data