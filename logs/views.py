import json
import uuid
#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, render
from django.core.urlresolvers import reverse

from datetime import datetime

from .forms import ManageLogForm, ManageLogUpdateInfoForm
from .models import Logs_by_location, Logs_by_update, Log_info_by_log, Log_file_info_by_log, Log_parameters_by_log, \
    Log_time_info_by_log, Log_update_schedule_by_log
from .logs import LogData
from qcs.models import Log_quality_control_schedule_by_log, Quality_control_info_by_log, \
    Quality_control_level_info_by_log
from qcs.qcs import QCData
from settings.base import TIME_ZONE
from utils import timemanager
from utils.tools import MiscTools

def location_logs(request):
    params = request.GET
    site_name = params.get('site_name', '')
    location_id = params.get('location_id', '')
    location_name = params.get('location_name', '')
    template = 'logs/location_logs.html'
    context = {
        'site_name' : site_name,
        'location_id' : location_id,
        'location_name' : location_name
    }
    return render(request, template, context)

def load_location_logs_json(request):
    params = request.GET
    location_id = params.get('location_id', '')
    log_name = params.get('log_name', '')
    json_request = params.get('json_request', '')
    logs_data = Logs_by_location.get_all_logs(location_id, log_name, json_request)
    return HttpResponse(json.dumps(logs_data), content_type='application/json')

def load_log_update_info_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    json_request = params.get('json_request', '')
    log_update_info_data = LogData.get_log_update_info(log_id, json_request)
    return HttpResponse(json.dumps(log_update_info_data), content_type='application/json')

def load_log_time_info_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    json_request = params.get('json_request', '')
    log_time_info_data = Log_time_info_by_log.get_log_time_info(log_id, json_request)
    return HttpResponse(json.dumps(log_time_info_data), content_type='application/json')

def load_log_file_info_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_file_info_data = Log_file_info_by_log.get_log_file_info(log_id)
    return HttpResponse(json.dumps(log_file_info_data), content_type='application/json')

def load_log_parameters_info_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_params_info_data = Log_parameters_by_log.get_log_parameters(log_id)
    return HttpResponse(json.dumps(log_params_info_data), content_type='application/json')

def manage_log(request):
    params = request.GET
    site_name = params.get('site_name', '')
    location_id = params.get('location_id', '')
    location_name = params.get('location_name', '')
    log_id = params.get('log_id', '')
    init_log_name = params.get('log_name', '')
    init_location_id_name = location_name + ": " + location_id
    init_log_form = dict
    template = 'logs/manage_log.html'

    if log_id:    #: Edit existing log
        log_data = Log_info_by_log.get_log(log_id)
        if log_data:
            log_map = log_data[0]
            init_log_description = log_map.get('log_description')
            init_log_form = {
                'location' : init_location_id_name,
                'log_id' : log_id,
                'log_name' : init_log_name,
                'log_description' : init_log_description
            }
        else:
            print("Couldn't load log info from database!")
    else:   #: Add new log
        init_log_form = {'location' : init_location_id_name}

    form = ManageLogForm(request.POST or None, initial=init_log_form)

    if form.is_valid():
        log_name = form.cleaned_data['log_name']
        log_description = form.cleaned_data['log_description']
        if not log_id:
            log_id = uuid.uuid4()
            Logs_by_location.create(
                location_id=location_id,
                log_name=log_name,
                log_description=log_description,
                log_id=log_id
            )
            Log_info_by_log.create(
                log_id=log_id,
                log_name=log_name,
                log_description=log_description
            )
        else:
            try:
                Logs_by_location(location_id=location_id, log_name=init_log_name).update(
                    log_name=log_name,
                    log_description=log_description
                )
                Log_info_by_log(log_id=log_id).update(
                    log_name=log_name,
                    log_description=log_description
                )
            except:
                print("Update query failed!")

        url = reverse('logs:location_logs')
        url += '?site_name=' + site_name
        url += '&location_id=' + MiscTools.uuid_to_str(location_id)
        url += '&location_name=' + location_name

        return HttpResponseRedirect(url)

    context = {
        'site_name' : site_name,
        'location_id' : location_id,
        'location_name' : location_name,
        'log_id' : log_id,
        'log_name' : init_log_name,
        'form' : form
    }

    return render(request, template, context)

def delete_log(request):
    params = request.GET
    site_name = params.get('site_name', '')
    location_id = params.get('location_id', '')
    location_name = params.get('location_name', '')
    log_id = params.get('log_id', '')
    log_name = params.get('log_name', '')

    logs_data = Logs_by_location.get_all_logs(location_id, log_name)
    if logs_data:
        try:
            Logs_by_location(location_id=location_id, log_name=log_name).delete()
        except:
            print("Delete location logs query failed!")
    else:
        print("Couldn't load logs from database!")

    log_info_data = Log_info_by_log.get_log(log_id)
    if log_info_data:
        try:
            Log_info_by_log(log_id=log_id).delete()
        except:
            print("Delete log query failed!")
    else:
        print("Couldn't load log info from database!")

    log_file_info_data = Log_file_info_by_log.get_log_file_info(log_id)
    if log_file_info_data:
        try:
            Log_file_info_by_log(log_id=log_id).delete()
        except:
            print("Delete log file info query failed!")
    else:
        print("Couldn't load log file info from database!")

    log_parameters_info_data = Log_parameters_by_log.get_log_parameters(log_id)
    if log_parameters_info_data:
        try:
            Log_parameters_by_log(log_id=log_id).delete()
        except:
            print("Delete log parameters info query failed!")
    else:
        print("Couldn't load log parameters info from database!")

    log_update_info_data = Log_update_schedule_by_log.get_log_updates(log_id)
    if log_update_info_data:
        try:
            Log_update_schedule_by_log(log_id=log_id).delete()
        except:
            print("Delete log update info query failed!")
    else:
        print("Couldn't load log update info from database!")

    active_logs_info_data = Logs_by_update.get_active_logs(log_id)
    disabled_logs_info_data = Logs_by_update.get_disabled_logs(log_id)
    logs_info_map = {}
    if active_logs_info_data:
        logs_info_map = active_logs_info_data[0]
    elif disabled_logs_info_data:
        logs_info_map = disabled_logs_info_data[0]
    if logs_info_map:
        try:
            Logs_by_update(log_update_is_active=logs_info_map.get('log_update_is_active'), log_id=log_id).delete()
        except:
            print("Delete log update info query failed!")

    log_time_info_data = Log_time_info_by_log.get_log_time_info(log_id)
    if log_time_info_data:
        try:
            Log_time_info_by_log(log_id=log_id).delete()
        except:
            print("Delete log time info query failed!")
    else:
        print("Couldn't load log time info from database!")

    log_qc_levels = QCData.get_log_qc_info(log_id)
    for qc_level_info in log_qc_levels:
        log_qc_level = qc_level_info.get('log_qc_level')
        try:
            Quality_control_info_by_log(log_id=log_id, qc_level=log_qc_level).delete()
        except:
            print("Exception in Quality_control_info_by_log")
        try:
            Quality_control_level_info_by_log(log_id=log_id).delete()
        except:
            print("Exception in Quality_control_level_info_by_log")
        try:
            Log_quality_control_schedule_by_log(log_id=log_id).delete()
        except:
            print("Exception in Log_quality_control_schedule_by_log")

    url = reverse('logs:location_logs')
    url += '?site_name=' + site_name
    url += '&location_id=' + MiscTools.uuid_to_str(location_id)
    url += '&location_name=' + location_name

    return HttpResponseRedirect(url)

def manage_log_update_info(request):
    params = request.GET
    site_name = params.get('site_name', '')
    location_id = params.get('location_id', '')
    location_name = params.get('location_name', '')
    log_id = params.get('log_id', '')
    log_name = params.get('log_name', '')

    # Set initial data

    log_file_info_data = Log_file_info_by_log.get_log_file_info(log_id)
    log_update_info_data = Log_update_schedule_by_log.get_log_updates(log_id)
    log_parameters_info_data = Log_parameters_by_log.get_log_parameters(log_id)
    log_time_info_data = Log_time_info_by_log.get_log_time_info(log_id)
    init_log_update_info_form = dict
    template = 'logs/manage_log_update_info.html'

    if log_file_info_data:    # Log file info already configured.
        log_file_info_map = log_file_info_data[0]
        log_file_path = log_file_info_map.get('log_file_path')
        log_file_line_num = log_file_info_map.get('log_file_line_num')
    else:   # Log file info not yet configured. Set default values.
        print("Setting default values for log file info..")
        log_file_path = None
        log_file_line_num = 1
    if log_update_info_data:     # Log update info already configured.
        log_update_info_map = log_update_info_data[0]
        log_update_is_active = log_update_info_map.get('log_update_is_active')
        log_last_update = log_update_info_map.get('log_last_update')
    else:   # Log file info not yet configured. Set default values.
        print("Setting default values for log update info..")
        log_update_is_active = False
        log_last_update = None
    if log_parameters_info_data:    # Log parameters info already configured.
        log_parameters_info_map = log_parameters_info_data[0]
        log_parameters = log_parameters_info_map.get('log_parameters')
        log_reading_types = log_parameters_info_map.get('log_reading_types')
    else:   # Log parameters info not yet configured. Set default values.
        print("Setting default values for log parameters info..")
        log_parameters = None
        log_reading_types = None
    if log_time_info_data:    # Log time info already configured.
        log_time_info_map = log_time_info_data[0]
        log_time_formats = log_time_info_map.get('log_time_formats')
        log_time_zone = log_time_info_map.get('log_time_zone')
    else:   # Log time info not yet configured. Set default values.
        print("Setting default values for log time info..")
        log_time_formats = None
        log_time_zone = TIME_ZONE   # Use server time zone configured in settings.base.py

    init_log_update_info_form = {
        'log_file_path' : log_file_path,
        'log_file_line_num' : log_file_line_num,
        'log_update_is_active' : log_update_is_active,
        'log_time_zone' : log_time_zone
    }

    form = ManageLogUpdateInfoForm(
        request.POST or None,
        initial=init_log_update_info_form,
        init_log_parameters=log_parameters,
        init_log_reading_types=log_reading_types,
        init_log_time_formats=log_time_formats
    )
    if form.is_valid():
        log_update_is_active = form.cleaned_data['log_update_is_active']
        log_file_path = form.cleaned_data['log_file_path']
        log_file_line_num = form.cleaned_data['log_file_line_num']
        log_time_zone = form.cleaned_data['log_time_zone']
        log_parameters, log_reading_types, log_time_formats = form.clean_parameters()

        Log_update_schedule_by_log.create(
            log_id=log_id,
            log_update_is_active=log_update_is_active,
            log_last_update=log_last_update
        )
        Logs_by_update.create(
            log_update_is_active=log_update_is_active,
            log_id=log_id,
            log_last_update=log_last_update
        )
        Log_file_info_by_log.create(
            log_id=log_id,
            log_file_path=log_file_path,
            log_file_line_num=log_file_line_num
        )
        Log_parameters_by_log.create(
            log_id=log_id,
            log_parameters=log_parameters,
            log_reading_types=log_reading_types
        )
        Log_time_info_by_log.create(
            log_id=log_id,
            log_time_formats=log_time_formats,
            log_time_zone=log_time_zone
        )
        url = reverse('logs:location_logs')
        url += '?site_name=' + site_name
        url += '&location_id=' + MiscTools.uuid_to_str(location_id)
        url += '&location_name=' + location_name
        return HttpResponseRedirect(url)

    context = {
        'site_name' : site_name,
        'location_id' : location_id,
        'location_name' : location_name,
        'log_id' : log_id,
        'log_name' : log_name,
        'form' : form
    }

    return render(request, template, context)