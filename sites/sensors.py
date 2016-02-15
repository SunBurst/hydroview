from .models import Sensors_by_location, Sensor_info_by_sensor

class SensorData(object):

    @classmethod
    def get_sensor(cls, sensor_name):

        sensor_data = []
        sensor_info = Sensor_info_by_sensor.objects.filter(sensor=sensor_name)

        for temp_sensor in sensor_info:
            temp_sensor_dict = {'sensor' : temp_sensor.sensor,
                                'description' : temp_sensor.description,
                                'file_path' : temp_sensor.file_path,
                                'file_line_num' : temp_sensor.file_line_num,
                                'parameters' : temp_sensor.parameters,
                                'time_ids' : temp_sensor.time_ids,
                                'time_zone' : temp_sensor.time_zone,
            }
            sensor_data.append(temp_sensor_dict)

        return sensor_data

    @classmethod
    def get_sensors_by_location(cls, location_name):

        sensors_data = []
        sensors_info = Sensors_by_location.objects.filter(location=location_name)

        for temp_sensor in sensors_info:
            temp_sensor_dict = {'location' : temp_sensor.location,
                                'sensor' : temp_sensor.sensor,
                                'sensor_num' : temp_sensor.sensor_num,
                                'description' : temp_sensor.description
            }
            sensors_data.append(temp_sensor_dict)

        return sensors_data

    @classmethod
    def get_sensor_nums(cls, location_name):

        sensor_nums = []
        sensors_info = Sensors_by_location.objects.filter(location=location_name)

        for temp_sensor in sensors_info:
            temp_sensor_dict = {
                                'sensor' : temp_sensor.sensor,
                                'sensor_num' : temp_sensor.sensor_num
            }
            sensor_nums.append(temp_sensor_dict)

        return sensor_nums

    @classmethod
    def get_sensor_num(cls, location_name, sensor_name):

        sensor_nums = cls.get_sensor_nums(location_name)
        num_match = None

        for sensor in sensor_nums:
            if (sensor.get('sensor') == sensor_name):
                num_match = sensor.get('sensor_num')
                return num_match

        return num_match
