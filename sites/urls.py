from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(
        regex=r'^(?P<site_name>.*)/(?P<location_name>.*)/',
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
        regex=r'^add/',
        view=views.location_add,
        name='location_add',
    ),
    url(
        regex=r'^location_new_post/',
        view=views.location_post,
        name='location_post',
    ),
    url(
        regex=r'^dashboard/',
        view=views.dashboard,
        name='dashboard',
    ),
]
