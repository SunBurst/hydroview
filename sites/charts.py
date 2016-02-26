import utils.timemanager as timemanager

#from .models import Parameters_by_sensor

class ChartData(object):

    @classmethod
    def get_parameter_data_by_day(cls, sensor_name, parameter, qc_level, days):#, user):
        tm = timemanager.TimeManager()
        series_data = []
        print(sensor_name,parameter,qc_level,days)
        rows = Parameters_by_sensor.objects.filter(sensor=sensor_name, parameter=parameter, qc_level=qc_level).limit(days)
        location_data = {"name" : sensor_name, "data" : []}

        for row in rows:
            time_ts_millis = tm.utc_dt_to_utc_ts_millis(row.time)
            value = row.value
            location_data["data"].append([time_ts_millis, value])

        series_data.append(location_data)
        return series_data