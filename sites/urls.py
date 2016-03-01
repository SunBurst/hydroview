from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(
        regex=r'^load_location/$',
        view=views.load_location,
        name='load_location',
    ),
    url(
        regex=r'^load_all_sites_json/$',
        view=views.load_all_sites_json,
        name='load_all_sites_json',
    ),
    url(
        regex=r'^load_site_locations_json/$',
        view=views.load_site_locations_json,
        name='load_site_locations_json',
    ),
    url(
        regex=r'^load_sensors_json/$',
        view=views.load_sensors_json,
        name='load_sensors_json',
    ),
    url(
        regex=r'^manage_logger_type/',
        view=views.manage_logger_type,
        name='manage_logger_type',
    ),
    #url(
    #    regex=r'^delete_logger_type/',
    #    view=views.delete_logger_type,
   #     name='delete_logger_type',
    #),
    url(
        regex=r'^manage_site/',
        view=views.manage_site,
        name='manage_site',
    ),
    url(
        regex=r'^delete_site/',
        view=views.delete_site,
        name='delete_site',
    ),
    url(
        regex=r'^manage_location/$',
        view=views.manage_location,
        name='manage_location',
    ),
    url(
        regex=r'^delete_location/$',
        view=views.delete_location,
        name='delete_location',
    ),
    url(
        regex=r'^manage_sensor/$',
        view=views.manage_sensor,
        name='manage_sensor',
    ),
    url(
        regex=r'^delete_sensor/$',
        view=views.delete_sensor,
        name='delete_sensor',
    ),
    url(
        regex=r'^chart_data_json/$',
        view=views.chart_data_json,
        name='chart_data_json',
    ),
]
