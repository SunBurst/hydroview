from django.core.exceptions import ValidationError
from settings.settings import VALID_FILE_EXTENTIONS

def validate_file_extension(value):
    import os
    if not (os.path.isfile(value)):
        raise ValidationError(u'File not found.')
    ext = os.path.splitext(value)[1]
    if not ext in VALID_FILE_EXTENTIONS:
        raise ValidationError(u'Unsupported file extension. Valid extentions are: ' + ", ".join(VALID_FILE_EXTENTIONS))
