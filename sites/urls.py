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
        regex=r'^load_sites_data/$',
        view=views.load_sites_data,
        name='load_sites_data',
    ),
    url(
        regex=r'^load_location_data/$',
        view=views.load_location_data,
        name='load_location_data',
    ),
    url(
        regex=r'^load_locations_data/$',
        view=views.load_locations_data,
        name='load_locations_data',
    ),
    url(
        regex=r'^chart_data_json/$',
        view=views.chart_data_json,
        name='chart_data_json',
    ),
    url(
        regex=r'^add_site/',
        view=views.add_site,
        name='add_site',
    ),
    url(
        regex=r'^edit_site/',
        view=views.edit_site,
        name='edit_site',
    ),
    url(
        regex=r'^dashboard/',
        view=views.dashboard,
        name='dashboard',
    ),
]
