from django.core.exceptions import ValidationError
from utils import parser

def validate_file_extension(value):
    static_data_parser = parser.CustomParser('static_data.ini')
    VALID_FILE_EXTENTIONS = (static_data_parser.get('VALIDATION', 'file_extentions'))
    if VALID_FILE_EXTENTIONS:
        VALID_FILE_EXTENTIONS = VALID_FILE_EXTENTIONS.replace(" ", "").split(",")
    import os
    if not (os.path.isfile(value)):
        raise ValidationError(u'File not found.')
    ext = os.path.splitext(value)[1]
    if VALID_FILE_EXTENTIONS and not ext in VALID_FILE_EXTENTIONS:
        raise ValidationError(u'Unsupported file extension. Valid extentions are: ' + ", ".join(VALID_FILE_EXTENTIONS))
