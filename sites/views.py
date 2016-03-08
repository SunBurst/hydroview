import json
import uuid
#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, HttpResponse, redirect, render
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta

from .charts import ChartData
from .forms import ManageLocationForm, ManageLogForm, ManageLogUpdateInfoForm, ManageLoggerTypeForm, ManageQCForm, \
    ManageSiteForm
from .locations import LocationData
from .loggers import LoggerData
from .logs import LogData
from .qcs import QCData
from .sites import SiteData
from .models import Locations_by_site, Location_info_by_location, Logger_types, Logger_type_by_logger_type, \
    Logger_time_format_by_logger_type, Logs_by_location, Log_info_by_log, Log_file_info_by_log, \
    Log_quality_control_schedule_by_log, Log_parameters_by_log, Log_time_info_by_log, Log_update_schedule_by_log, \
    Quality_controls, Quality_control_info_by_log, Quality_control_info_by_quality_control, \
    Quality_control_level_info_by_log, Sites, Site_info_by_site
from .management.commands import run_update
from utils.tools import MiscTools


###########################################################################
######################    API FOR LOADING TEMPLATES    ####################
###########################################################################

def index(request):
    template_name = 'sites/index.html'
    context = {}
    return render(request, template_name, context)

def location_info(request):
    params = request.GET
    site_id = params.get('site_id', '')
    location_id = params.get('location_id', '')

    site_data = SiteData.get_site(site_id)
    location_data = LocationData.get_location(location_id)
    try:
        site_data = site_data[0]
        location_data = location_data[0]
    except IndexError:
        print("Index error!")

    site_name = site_data.get('site_name')
    location_name = location_data.get('location_name')
    location_description = location_data.get('location_description')
    location_latitude = location_data.get('location_latitude')
    location_longitude = location_data.get('location_longitude')

    template = 'sites/location_info.html'
    context = {
        'site_name' : site_name,
        'location_name' : location_name,
        'location_description': location_description,
        'location_latitude' : location_latitude,
        'location_longitude' : location_longitude
    }
    return render(request, template, context)

def location_logs(request):
    params = request.GET
    site_name = params.get('site_name', '')
    location_id = params.get('location_id', '')
    location_name = params.get('location_name', '')
    template = 'sites/location_logs.html'
    context = {
        'site_name' : site_name,
        'location_id' : location_id,
        'location_name' : location_name
    }
    return render(request, template, context)

###########################################################################
#####################    API FOR RETURNING JSON DATA    ###################
###########################################################################

def load_all_sites_json(request):
    params = request.GET
    json_request = params.get('json_request', '')
    sites_data = SiteData.get_all_sites(json_request)
    return HttpResponse(json.dumps(sites_data), content_type='application/json')

def load_site_locations_json(request):
    params = request.GET
    site_id = params.get('site_id', '')
    location_name = params.get('location_name')
    json_request = params.get('json_request', '')
    locations_data = LocationData.get_all_locations(site_id, location_name, json_request)
    return HttpResponse(json.dumps(locations_data), content_type='application/json')

def load_location_logs_json(request):
    params = request.GET
    location_id = params.get('location_id', '')
    log_name = params.get('log_name', '')
    json_request = params.get('json_request', '')
    logs_data = LogData.get_all_logs(location_id, log_name, json_request)
    return HttpResponse(json.dumps(logs_data), content_type='application/json')

def load_log_update_info_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    json_request = params.get('json_request', '')
    log_file_info_data = LogData.get_log_update_info(log_id, json_request)
    return HttpResponse(json.dumps(log_file_info_data), content_type='application/json')

def load_log_time_info_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_time_info_data = LoggerData.get_log_time_info(log_id)
    return HttpResponse(json.dumps(log_time_info_data), content_type='application/json')

def load_log_parameters_info_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_params_info_data = LogData.get_log_parameters(log_id)
    return HttpResponse(json.dumps(log_params_info_data), content_type='application/json')

def load_log_qc_info_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    json_request = params.get('json_request', '')
    log_qc_info_data = QCData.get_log_qc_info(log_id, json_request)
    return HttpResponse(json.dumps(log_qc_info_data), content_type='application/json')

def load_log_qc_values_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_qc_level = params.get('qc_level', '')
    json_request = params.get('json_request', '')
    log_qc_values_data = QCData.get_log_qc_values(log_id, log_qc_level, json_request)
    return HttpResponse(json.dumps(log_qc_values_data), content_type='application/json')

def load_all_logger_types_json(request):
    logger_types_data = LoggerData.get_all_loggers()
    return HttpResponse(json.dumps(logger_types_data), content_type='application/json')

def load_all_quality_controls_json(request):
    quality_controls_data = QCData.get_all_qcs()
    return HttpResponse(json.dumps(quality_controls_data), content_type='application/json')

###########################################################################
#######################    API FOR MANAGING FORMS    ######################
###########################################################################

def manage_logger_type(request):
    params = request.GET
    init_logger_type_name = params.get('logger_type_name', '')
    init_logger_type_form = dict
    init_logger_time_formats = []
    template = 'sites/manage_logger_type.html'

    if init_logger_type_name:    #: Edit existing logger type
        logger_type_data = LoggerData.get_logger(init_logger_type_name)
        try:
            logger_type_data = logger_type_data[0]
        except IndexError:
            print("Index error!")
        init_logger_description = logger_type_data.get('logger_type_description')
        init_logger_time_formats = logger_type_data.get('logger_time_formats')

        init_logger_type_form = {
            'logger_type_name' : init_logger_type_name,
            'logger_type_description' : init_logger_description,
        }
    else:   #: Add new logger type
        init_logger_type_form = {}

    form = ManageLoggerTypeForm(request.POST or None, initial=init_logger_type_form, init_logger_time_formats=init_logger_time_formats)

    if form.is_valid():
        logger_type_name = form.cleaned_data['logger_type_name']
        logger_type_description = form.cleaned_data['logger_type_description']
        logger_time_formats_ids = form.clean_time_formats()
        logger_time_formats = list(logger_time_formats_ids.keys())

        if init_logger_type_name:
            try:
                Logger_types(bucket=0, logger_type_name=init_logger_type_name).delete()
                Logger_type_by_logger_type(logger_type_name=init_logger_type_name).delete()
                Logger_time_format_by_logger_type(logger_type_name=init_logger_type_name).delete()
            except:
                print("Delete query failed!")

        Logger_types.create(
            bucket=0,
            logger_type_name=logger_type_name,
            logger_type_description=logger_type_description
        )
        Logger_type_by_logger_type.create(
            logger_type_name=logger_type_name,
            logger_type_description=logger_type_description,
            logger_time_formats=logger_time_formats
        )
        for time_fmt, time_ids in logger_time_formats_ids.items():
            Logger_time_format_by_logger_type.create(
                logger_type_name=logger_type_name,
                logger_time_format=time_fmt,
                logger_time_ids=time_ids
            )
        url = reverse('sites:index')

        return HttpResponseRedirect(url)

    context = {
        'logger_type_name' : init_logger_type_name,
        'form' : form
    }

    return render(request, template, context)

def delete_logger_type(request):
    params = request.GET
    logger_type_name = params.get('logger_type_name', '')
    try:
        Logger_types(bucket=0, logger_type_name=logger_type_name).delete()
        Logger_type_by_logger_type(logger_type_name=logger_type_name).delete()
        Logger_time_format_by_logger_type(logger_type_name=logger_type_name).delete()
    except:
        print("Delete query failed!")

    url = reverse('sites:index')

    return HttpResponseRedirect(url)

def manage_quality_control(request):
    params = request.GET
    init_qc_level = params.get('qc_level', '')
    init_qc_name = params.get('qc_name', '')
    init_qc_form = dict
    template = 'sites/manage_quality_control.html'

    if init_qc_level:    #: Edit existing quality control
        quality_control_data = QCData.get_qc(init_qc_level)
        try:
            quality_control_data = quality_control_data[0]
        except IndexError:
            print("Index error!")
        init_qc_name = quality_control_data.get('qc_name')
        init_qc_description = quality_control_data.get('qc_description')

        init_qc_form = {
            'qc_level' : init_qc_level,
            'qc_name' : init_qc_name,
            'qc_description' : init_qc_description,
        }
    else:   #: Add new quality control
        init_qc_form = {}

    form = ManageQCForm(request.POST or None, initial=init_qc_form)

    if form.is_valid():
        qc_level = form.cleaned_data['qc_level']
        qc_name = form.cleaned_data['qc_name']
        qc_description = form.cleaned_data['qc_description']

        if init_qc_level:
            try:
                Quality_controls(bucket=0, qc_level=init_qc_level).delete()
                Quality_control_info_by_quality_control(qc_level=init_qc_level).delete()
            except:
                print("Delete query failed!")

        Quality_controls.create(
            bucket=0,
            qc_level=qc_level,
            qc_name=qc_name,
            qc_description=qc_description
        )
        Quality_control_info_by_quality_control.create(
            qc_level=qc_level,
            qc_name=qc_name,
            qc_description=qc_description
        )
        url = reverse('sites:index')

        return HttpResponseRedirect(url)

    context = {
        'qc_level' : init_qc_level,
        'qc_name' : init_qc_name,
        'form' : form
    }

    return render(request, template, context)

def delete_quality_control(request):
    params = request.GET
    qc_level = params.get('qc_level', '')
    try:
        Quality_controls(bucket=0, qc_level=qc_level).delete()
        Quality_control_info_by_quality_control(qc_level=qc_level).delete()
    except:
        print("Delete query failed!")

    url = reverse('sites:index')

    return HttpResponseRedirect(url)

def manage_site(request):
    params = request.GET
    site_id = params.get('site_id', '')
    site_name = params.get('site_name', '')
    init_site_form = dict
    template = 'sites/manage_site.html'

    if site_id:    #: Edit existing site
        site_data = SiteData.get_site(site_id)
        try:
            site_data = site_data[0]
        except IndexError:
            print("Index error!")
        init_site_name = site_data.get('site_name')
        init_site_description = site_data.get('site_description')
        init_site_latitude = site_data.get('site_latitude')
        init_site_longitude = site_data.get('site_longitude')

        init_site_form = {
            'site_name' : init_site_name,
            'site_description' : init_site_description,
            'site_latitude' : init_site_latitude,
            'site_longitude' : init_site_longitude
        }

    else:   #: Add new site
        init_site_form = {}

    form = ManageSiteForm(request.POST or None, initial=init_site_form)

    if form.is_valid():
        site_name = form.cleaned_data['site_name']
        site_description = form.cleaned_data['site_description']
        site_position = form.clean_gps_coordinates()

        if not site_id:
            site_id = uuid.uuid4()
        else:
            Sites(bucket=0, site_id=site_id).delete()
            Site_info_by_site(site_id=site_id).delete()

        Sites.create(
            bucket=0,
            site_id=site_id,
            site_name=site_name,
            site_description=site_description,
            site_position = site_position
        )
        Site_info_by_site.create(
            site_id=site_id,
            site_name=site_name,
            site_description=site_description,
            site_position = site_position
        )

        url = reverse('sites:index')

        return HttpResponseRedirect(url)

    context = {
        'site_id' : site_id,
        'site_name' : site_name,
        'form' : form
    }

    return render(request, template, context)

def delete_site(request):
    params = request.GET
    site_id = params.get('site_id', '')
    try:
        Sites(bucket=0, site_id=site_id).delete()
        Site_info_by_site(site_id=site_id).delete()
    except:
        print("Couldn't delete site!")

    url = reverse('sites:index')
    return HttpResponseRedirect(url)

def manage_location(request):
    params = request.GET
    site_id = params.get('site_id', '')
    site_name = params.get('site_name', '')
    location_id = params.get('location_id', '')
    location_name = params.get('location_name', '')
    init_location_form = dict
    template = 'sites/manage_location.html'

    if location_id:    #: Edit existing location
        location_data = LocationData.get_location(location_id)
        try:
            location_data = location_data[0]
        except IndexError:
            print("Index error!")

        init_location_name = location_data.get('location_name')
        init_location_latitude = location_data.get('location_latitude')
        init_location_longitude = location_data.get('location_longitude')
        init_location_description = location_data.get('location_description')

        init_location_form = {
            'site_name' : site_name,
            'location_name' : init_location_name,
            'location_latitude' : init_location_latitude,
            'location_longitude' : init_location_longitude,
            'location_description' : init_location_description
        }

    else:   #: Add new location
        try:
            target_site = SiteData.get_site(site_id)[0]
            site_name = target_site.get('site_name')
            init_location_form = {'site_name' : site_name}
        except IndexError:
            print("Index error!")

    form = ManageLocationForm(request.POST or None, initial=init_location_form)

    if form.is_valid():
        location_name = form.cleaned_data['location_name']
        location_description = form.cleaned_data['location_description']
        location_position = form.clean_gps_coordinates()
        temp_location_name = location_name
        temp_site_location = LocationData.get_all_locations(site_id, temp_location_name)

        if not location_id:
            location_id = uuid.uuid4()
        else:
            Locations_by_site(site_id=site_id, location_name=location_name).delete()
            Location_info_by_location(location_id=location_id).delete()

        Locations_by_site.create(
            site_id=site_id,
            location_name=location_name,
            location_id=location_id,
            location_description=location_description,
            location_position=location_position
        )
        Location_info_by_location.create(
            location_id=location_id,
            location_name=location_name,
            location_description=location_description,
            location_position=location_position
        )

        url = reverse('sites:location_info')
        url += '?site_id=' + MiscTools.uuid_to_str(site_id)
        if location_id:
            url += '&location_id=' + MiscTools.uuid_to_str(location_id)

        return HttpResponseRedirect(url)

    context = {
        'site_id' : site_id,
        'site_name' : site_name,
        'location_id' : location_id,
        'location_name' : location_name,
        'form' : form
    }

    return render(request, template, context)

def delete_location(request):
    params = request.GET
    site_id = params.get('site_id', '')
    location_id = params.get('location_id', '')
    location_name = params.get('location_name', '')
    try:
        Locations_by_site(site_id=site_id, location_name=location_name).delete()
        Location_info_by_location(location_id=location_id).delete()
    except:
        print("Couldn't delete location!")
    url = reverse('sites:index')
    return HttpResponseRedirect(url)

def manage_log(request):
    params = request.GET
    site_name = params.get('site_name', '')
    location_id = params.get('location_id', '')
    location_name = params.get('location_name', '')
    log_id = params.get('log_id', '')
    log_name = params.get('log_name', '')
    init_log_form = dict
    template = 'sites/manage_log.html'

    if log_id:    #: Edit existing log
        log_data = LogData.get_log(log_id)
        try:
            log_data = log_data[0]
        except IndexError:
            print("Index error!")
        init_log_name = log_data.get('log_name')
        init_log_description = log_data.get('log_description')
        init_log_form = {
            'location_name' : location_name,
            'log_name' : init_log_name,
            'log_description' : init_log_description
        }

    else:   #: Add new log
        init_log_form = {'location_name' : location_name}

    form = ManageLogForm(request.POST or None, initial=init_log_form)

    if form.is_valid():
        log_name = form.cleaned_data['log_name']
        log_description = form.cleaned_data['log_description']
        temp_log_name = log_name
        temp_location_log = LogData.get_all_logs(location_id, temp_log_name)

        log_file_path = None
        log_file_line_num = 0
        log_last_update = None
        log_next_update = None
        logger_type_name = None
        logger_time_format = None
        logger_time_ids = None
        log_time_zone = None
        log_parameters = None
        log_reading_types = None

        if not temp_location_log:

            if not log_id:
                log_id = uuid.uuid4()
            else:
                try:
                    log_update_info_data = LogData.get_log_update_info(log_id)
                    log_update_info_data = log_update_info_data[0]
                    log_logger_type_info_data = LoggerData.get_log_time_info(log_id)
                    log_logger_type_info_data = log_logger_type_info_data[0]
                    log_parameters_info_data = LogData.get_log_parameters(log_id)
                    log_parameters_info_data = log_parameters_info_data[0]
                    log_file_path = log_update_info_data.get('log_file_path')
                    log_file_line_num = log_update_info_data.get('log_file_line_num', 0)
                    log_last_update = log_update_info_data.get('log_last_update')
                    log_next_update = log_update_info_data.get('log_next_update')
                    logger_type_name = log_logger_type_info_data.get('logger_type_name')
                    logger_time_format = log_logger_type_info_data.get('logger_time_format')
                    logger_time_ids = log_logger_type_info_data.get('logger_time_ids')
                    log_time_zone = log_logger_type_info_data.get('log_time_zone')
                    log_parameters = log_parameters_info_data.get('log_parameters')
                    log_reading_types = log_parameters_info_data.get('log_reading_types')

                except IndexError:
                    print("Index error!")
                Logs_by_location(location_id=location_id, log_name=log_name).delete()
                Log_info_by_log(log_id=log_id).delete()
                Log_file_info_by_log(log_id=log_id).delete()
                Log_update_schedule_by_log(log_id=log_id).delete()
                Log_time_info_by_log(log_id=log_id).delete()
                Log_parameters_by_log(log_id=log_id).delete()

            Logs_by_location.create(
                location_id=location_id,
                log_name=log_name,
                log_id=log_id,
                log_description=log_description
            )
            Log_info_by_log.create(
                log_id=log_id,
                log_name=log_name,
                log_description=log_description
            )
            Log_file_info_by_log.create(
                log_id=log_id,
                log_file_path=log_file_path,
                log_file_line_num=log_file_line_num
            )
            Log_update_schedule_by_log.create(
                log_id=log_id,
                log_last_update=log_last_update,
                log_next_update=log_next_update
            )
            Log_time_info_by_log.create(
                log_id=log_id,
                logger_type_name=logger_type_name,
                logger_time_format=logger_time_format,
                logger_time_ids=logger_time_ids,
                log_time_zone=log_time_zone
            )
            Log_parameters_by_log.create(
                log_id=log_id,
                log_parameters=log_parameters,
                log_reading_types=log_reading_types,
            )
        url = reverse('sites:location_logs')
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

def delete_log(request):
    params = request.GET
    site_name = params.get('site_name', '')
    location_id = params.get('location_id', '')
    location_name = params.get('location_name', '')
    log_id = params.get('log_id', '')
    log_name = params.get('log_name', '')
    log_qc_levels = QCData.get_log_qc_info(log_id)
    try:
        Logs_by_location(location_id=location_id, log_name=log_name).delete()
        Log_info_by_log(log_id=log_id).delete()
        Log_file_info_by_log(log_id=log_id).delete()
        Log_parameters_by_log(log_id=log_id).delete()
        Log_update_schedule_by_log(log_id=log_id).delete()
        Log_quality_control_schedule_by_log(log_id=log_id).delete()
        Log_time_info_by_log(log_id=log_id).delete()
        for qc_level_info in log_qc_levels:
            log_qc_level = qc_level_info.get('log_qc_level')
            Quality_control_info_by_log(log_id=log_id, qc_level=log_qc_level).delete()
        Quality_control_level_info_by_log(log_id=log_id).delete()
    except:
        print("Couldn't delete log!")
    url = reverse('sites:location_logs')
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
    init_log_update_info_form = dict
    template = 'sites/manage_log_update_info.html'
    log_update_info_data = LogData.get_log_update_info(log_id)
    log_file_info_data = LoggerData.get_log_time_info(log_id)
    log_parameters = LogData.get_log_parameters(log_id)
    init_logger_types = LoggerData.get_logger_info()

    try:
        log_update_info_data = log_update_info_data[0]
        log_file_info_data = log_file_info_data[0]
        log_parameters = log_parameters[0]
    except IndexError:
        print("Index error!")

    init_log_last_update = log_update_info_data.get('log_last_update')
    init_log_next_update = log_update_info_data.get('log_next_update')
    init_log_update_interval = None
    init_log_update_is_active = False

    if init_log_next_update:
        init_log_update_is_active = True
        init_log_update_interval = datetime.time(init_log_next_update)

    init_logger_type_name = log_file_info_data.get('logger_type_name')
    init_logger_time_format = log_file_info_data.get('logger_time_format')
    init_logger_time_ids = log_file_info_data.get('logger_time_ids')
    init_log_time_zone = log_file_info_data.get('log_time_zone')
    init_log_update_info_form = {
        'log_file_path' : log_update_info_data.get('log_file_path'),
        'log_file_line_num' : log_update_info_data.get('log_file_line_num'),
        'update_is_active' : init_log_update_is_active,
        'update_interval' : init_log_update_interval,
        'logger_type_name' : init_logger_type_name,
        #'logger_time_format' : init_logger_time_format,
        #'logger_time_ids' : init_logger_time_ids,
        #'log_time_zone' : init_log_time_zone
    }

    form = ManageLogUpdateInfoForm(request.POST or None, initial=init_log_update_info_form, init_logger_types=init_logger_types)

    if form.is_valid():
        log_next_update = form.get_next_update()
        log_file_line_num = form.cleaned_data['log_file_line_num']
        log_file_path = form.cleaned_data['log_file_path']
        try:
            Log_file_info_by_log(log_id=log_id).delete()
            Log_update_schedule_by_log(log_id=log_id).delete()
        except:
            print("Couldn't delete log update info!")
        Log_file_info_by_log.create(
            log_id=log_id,
            log_file_path=log_file_path,
            log_file_line_num=log_file_line_num
        )
        Log_update_schedule_by_log.create(
            log_id=log_id,
            log_last_update=init_log_last_update,
            log_next_update=log_next_update
        )
        # fire off update
        url = reverse('sites:location_logs')
        url += '?site_name=' + site_name
        url += '&location_id=' + MiscTools.uuid_to_str(location_id)
        url += '&location_name=' + location_name
        return HttpResponseRedirect(url)

    context = {
        'site_name' : site_name,
        'location_id' : location_id,
        'location_name' : location_name,
        'log_name' : log_name,
        'form' : form
    }

    return render(request, template, context)

def manage_log_time_info(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_name = params.get('log_name', '')
    template = 'sites/manage_log_time_info.html'
    return render(request, template, {})

def manage_log_parameters_info(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_name = params.get('log_name', '')
    template = 'sites/manage_log_parameters_info.html'
    return render(request, template, {})

def manage_log_qc_info(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_name = params.get('log_name', '')
    template = 'sites/manage_log_qc_info.html'
    return render(request, template, {})

def manage_log_qc_values(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_name = params.get('log_name', '')
    template = 'sites/manage_log_qc_values.html'
    return render(request, template, {})

def manage_log1(request):
    params = request.GET
    site_id = params.get('site_id', '')
    location_id = params.get('location_id', '')
    log_id = params.get('log_id', '')
    init_log_form = dict
    #init_sensor_last_update = None
    template = 'sites/manage_sensor.html'

    if sensor_name:    #: Edit existing sensor

        sensor_num = LogData.get_sensor_num(location_name, sensor_name)
        sensor_data_list = LogData.get_sensor(sensor_name)
        sensor_data = sensor_data_list[0]

        init_sensor_location = location_name
        init_sensor_num = sensor_num
        init_sensor_name = sensor_data.get('sensor')
        init_sensor_description = sensor_data.get('description')
        init_sensor_last_update = sensor_data.get('last_update')
        init_sensor_next_update = sensor_data.get('next_update')
        init_sensor_file_path = sensor_data.get('file_path')
        init_sensor_file_line_num = sensor_data.get('file_line_num')
        init_sensor_time_format = sensor_data.get('time_format')
        init_sensor_time_zone = sensor_data.get('time_zone')
        init_sensor_params_list = sensor_data.get('parameters')
        init_sensor_params = ",".join(init_sensor_params_list)
        init_sensor_time_ids = sensor_data.get('time_ids')

        init_sensor_update_interval = None
        init_sensor_update_is_active = False
        if init_sensor_next_update:
            init_sensor_update_is_active = True
            init_sensor_update_interval = datetime.time(init_sensor_next_update)


        init_sensor_form = {
                            'location' : init_sensor_location,
                            'sensor_num' : init_sensor_num,
                            'sensor' : init_sensor_name,
                            'description' : init_sensor_description,
                            'update_is_active' : init_sensor_update_is_active,
                            'update_interval' : init_sensor_update_interval,
                            'file_path' : init_sensor_file_path,
                            'file_line_num' : init_sensor_file_line_num,
                            'time_format' : init_sensor_time_format,
                            'time_zone' : init_sensor_time_zone,
                            'time_ids' : init_sensor_time_ids,
                            'parameters' : init_sensor_params
        }

    else:   #: Add new sensor
        init_sensor_form = {'location' : location_name}

    form = ManageSensorForm(request.POST or None, initial=init_sensor_form)

    if form.is_valid():
        if sensor_name:
            Sensors_by_location(location=location_name, sensor=sensor_name).delete()
            Sensor_info_by_sensor(sensor=sensor_name).delete()

        sensor_num = form.cleaned_data['sensor_num']
        sensor_name = form.cleaned_data['sensor']
        sensor_description = form.cleaned_data['description']
        sensor_next_update = form.get_next_update()
        sensor_file_line_num = form.cleaned_data['file_line_num']
        sensor_file_path = form.cleaned_data['file_path']
        sensor_time_format = form.cleaned_data['time_format']
        sensor_time_zone = form.cleaned_data['time_zone']
        sensor_time_ids = form.clean_time_ids()
        sensor_params = form.cleaned_data['parameters'].split(',')
        sensor_time_info = {
                            'time_format' : sensor_time_format,
                            'time_zone' : sensor_time_zone,
                            'time_ids' : sensor_time_ids
        }

        Sensors_by_location.create(
            location=location_name,
            sensor=sensor_name,
            sensor_num=sensor_num,
            description=sensor_description
        )

        Sensor_info_by_sensor.create(
            sensor=sensor_name,
            description=sensor_description,
            file_path=sensor_file_path,
            file_line_num=sensor_file_line_num,
            parameters=sensor_params,
            time_info=sensor_time_info,
            last_update=init_sensor_last_update,
            next_update=sensor_next_update
        )

        if sensor_next_update:
            run_update.check_sensor_update(sensor_name)

        url = reverse('sites:load_location')
        url += '?site_name=' + site_name + '&location_name=' + location_name

        return HttpResponseRedirect(url)

    context = {
        'site_name' : site_name,
        'location_name' : location_name,
        'form' : form
    }

    return render(request, template, context)

def delete_sensor(request):

    params = request.GET

    site_name = params.get('site_name', '')
    location_name = params.get('location_name', '')
    sensor_name = params.get('sensor_name', '')

    Sensors_by_location(location=location_name).delete()
    Sensor_info_by_sensor(sensor=sensor_name).delete()

    url = reverse('sites:load_location')
    url += '?site_name=' + site_name + '&location_name=' + location_name

    return HttpResponseRedirect(url)

###########################################################################
######################    API FOR MANAGING CHARTS    ######################
###########################################################################

def chart_data_json(request):

    params = request.GET

    days = params.get('days', 0)
    sensor_name = params.get('sensor_name')
    parameter = params.get('parameter')
    qc_level = params.get('qc_level')
    qc_level = int(qc_level)
    days=int(days)
    data = ChartData.get_parameter_data_by_day(sensor_name, parameter, qc_level, days)

    return HttpResponse(json.dumps(data), content_type='application/json')




