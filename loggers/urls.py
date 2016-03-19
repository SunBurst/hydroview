from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        regex=r'^load_all_logger_time_formats_json/$',
        view=views.load_all_logger_time_formats_json,
        name='load_all_logger_time_formats_json',
    ),
    url(
        regex=r'^load_logger_time_format_json/$',
        view=views.load_logger_time_format_json,
        name='load_logger_time_format_json',
    ),
    url(
        regex=r'^manage_logger_time_format/$',
        view=views.manage_logger_time_format,
        name='manage_logger_time_format',
    ),
    url(
        regex=r'^delete_logger_time_format/',
        view=views.delete_logger_time_format,
        name='delete_logger_time_format',
    ),
]