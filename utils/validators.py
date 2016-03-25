from django.core.exceptions import ValidationError

def validate_decimal_number(value):
    value = value.replace(",", ".")
    try:
        float_value = float(value)
        return float_value
    except ValueError:
        raise ValidationError(u"{0} is not a valid decimal number!". format(value))

def validate_wgs84_latitude(value):
    latitude_value = validate_decimal_number(value)
    if (latitude_value > 90.0 or latitude_value < -90.0):
        raise ValidationError(u"{0} is not a valid WGS 84 latitude representation!")

def validate_wgs84_longitude(value):
    longitude_value = validate_decimal_number(value)
    if (longitude_value > 180.0 or longitude_value < -180.0):
        raise ValidationError(u"{0} is not a valid WGS 84 longitude representation!")
