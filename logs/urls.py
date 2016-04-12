
from django.conf.urls import url


from . import views

urlpatterns = [
    url(
        regex=r'^load_location_logs_json/$',
        view=views.load_location_logs_json,
        name='load_location_logs_json',
    ),
    url(
        regex=r'^load_log_update_info_json/$',
        view=views.load_log_update_info_json,
        name='load_log_update_info_json',
    ),
    url(
        regex=r'^load_log_time_info_json/$',
        view=views.load_log_time_info_json,
        name='load_log_time_info_json',
    ),
    url(
        regex=r'^load_log_file_info_json/$',
        view=views.load_log_file_info_json,
        name='load_log_file_info_json',
    ),
    url(
        regex=r'^load_log_parameters_info_json/$',
        view=views.load_log_parameters_info_json,
        name='load_log_parameters_info_json',
    ),
    url(
        regex=r'^location_logs/$',
        view=views.location_logs,
        name='location_logs',
    ),
    url(
        regex=r'^manage_log/$',
        view=views.manage_log,
        name='manage_log',
    ),
    url(
        regex=r'^delete_log/$',
        view=views.delete_log,
        name='delete_log',
    ),
    url(
        regex=r'^manage_log_update_info/$',
        view=views.manage_log_update_info,
        name='manage_log_update_info',
    ),
]