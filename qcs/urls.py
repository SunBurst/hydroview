from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        regex=r'^load_all_quality_controls_json/$',
        view=views.load_all_quality_controls_json,
        name='load_all_quality_controls_json',
    ),
        url(
        regex=r'^load_log_qc_info_json/$',
        view=views.load_log_qc_info_json,
        name='load_log_qc_info_json',
    ),
    url(
        regex=r'^load_log_qc_values_json/$',
        view=views.load_log_qc_values_json,
        name='load_log_qc_values_json',
    ),
    url(
        regex=r'^manage_quality_control/$',
        view=views.manage_quality_control,
        name='manage_quality_control',
    ),
    url(
        regex=r'^delete_quality_control/$',
        view=views.delete_quality_control,
        name='delete_quality_control',
    ),
    url(
        regex=r'^manage_log_qc_info/$',
        view=views.manage_log_qc_info,
        name='manage_log_qc_info',
    ),
    url(
        regex=r'^manage_log_qc_values/$',
        view=views.manage_log_qc_values,
        name='manage_log_qc_values',
    ),
]