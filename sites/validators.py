from django.core.exceptions import ValidationError

def validate_file_extension(field):
    import os
    ext = os.path.splitext(field.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv', '.dat']
    if not ext in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')