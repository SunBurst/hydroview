from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(
        regex=r'^load_all_sites_json/$',
        view=views.load_all_sites_json,
        name='load_all_sites_json',
    ),
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
        regex=r'^chart_data_json/$',
        view=views.chart_data_json,
        name='chart_data_json',
    ),
]
