from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        regex=r'^location_info/$',
        view=views.location_info,
        name='location_info',
    ),
    url(
        regex=r'^load_site_locations_json/$',
        view=views.load_site_locations_json,
        name='load_site_locations_json',
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
]