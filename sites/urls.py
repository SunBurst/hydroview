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
        regex=r'^load_sites_json/$',
        view=views.load_sites_json,
        name='load_sites_json',
    ),
    url(
        regex=r'^load_locations_json/$',
        view=views.load_locations_json,
        name='load_locations_json',
    ),
    url(
        regex=r'^load_sensors_json/$',
        view=views.load_sensors_json,
        name='load_sensors_json',
    ),
    url(
        regex=r'^manage_site/',
        view=views.manage_site,
        name='manage_site',
    ),
    url(
        regex=r'^manage_location/',
        view=views.manage_location,
        name='manage_location',
    ),
    url(
        regex=r'^manage_sensor/$',
        view=views.manage_sensor,
        name='manage_sensor',
    ),
    url(
        regex=r'^chart_data_json/$',
        view=views.chart_data_json,
        name='chart_data_json',
    ),
    #url(
    #    regex=r'^dashboard/',
    #    view=views.dashboard,
    #    name='dashboard',
    #),
]
