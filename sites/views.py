import json
import uuid
#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, HttpResponse, redirect, render
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta

from .charts import ChartData
from .forms import ManageLocationForm, ManageLoggerTypeForm, ManageQCForm, ManageSensorForm, ManageSiteForm
from .locations import LocationData
from .loggers import LoggerData
from .logs import LogData
from .qcs import QCData
from .sites import SiteData
from .models import Locations_by_site, Location_info_by_location, Logger_types, Logger_type_by_logger_type, \
    Logger_time_format_by_logger_type, Quality_controls, Quality_control_info_by_quality_control, \
    Sites, Site_info_by_site
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

###########################################################################
#####################    API FOR RETURNING JSON DATA    ###################
###########################################################################

def date_handler(dt):
    return dt.isoformat() if hasattr(dt, 'isoformat') else dt

def load_all_sites_json(request):
    params = request.GET
    json_request = params.get('json_request', '')
    sites_data = SiteData.get_all_sites(json_request)
    return HttpResponse(json.dumps(sites_data), content_type='application/json')

def load_site_locations_json(request):
    params = request.GET
    location_name = params.get('location_name')
    json_request = params.get('json_request', '')
    site_id = params.get('site_id', '')
    locations_data = LocationData.get_all_locations(site_id, location_name, json_request)
    return HttpResponse(json.dumps(locations_data), content_type='application/json')

def load_sensors_json(request):

    params = request.GET
    location_name = params.get('location_name', '')
    sensors_data = LogData.get_sensors_by_location(location_name)
    location_sensors_data = []

    for sensor in sensors_data:
        sensor_name = sensor.get('sensor')
        sensor_info = LogData.get_sensor(sensor_name)
        temp_sensor_dict = sensor_info[0]
        temp_last_update = date_handler(temp_sensor_dict.get('last_update'))
        temp_next_update = date_handler(temp_sensor_dict.get('next_update'))
        temp_sensor_dict['last_update'] = temp_last_update
        temp_sensor_dict['next_update'] = temp_next_update
        location_sensors_data.append(temp_sensor_dict)

    return HttpResponse(json.dumps(location_sensors_data), content_type='application/json')

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
    template = 'sites/manage_logger_type.html'

    if init_qc_level:    #: Edit existing quality control
        quality_control_data = QCData.get_qc(init_qc_level)
        try:
            quality_control_data = quality_control_data[0]
        except IndexError:
            print("Index error!")
        init_qc_name = quality_control_data.get('qc_name')
        init_qc_description = quality_control_data.get('qc_description')
        init_qc_replacement_value = quality_control_data.get('qc_replacement_value')

        init_qc_form = {
            'qc_level' : init_qc_level,
            'qc_name' : init_qc_name,
            'qc_description' : init_qc_description,
            'qc_replacement_value' : init_qc_replacement_value
        }
    else:   #: Add new quality control
        init_qc_form = {}

    form = ManageQCForm(request.POST or None, initial=init_qc_form)

    if form.is_valid():
        qc_level = form.cleaned_data['qc_level']
        qc_name = form.cleaned_data['qc_name']
        qc_description = form.cleaned_data['qc_description']
        qc_replacement_value = form.cleaned_data['qc_replacement_value']

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
            qc_description=qc_description,
        )
        Quality_control_info_by_quality_control.create(
            qc_level=qc_level,
            qc_name=qc_name,
            qc_description=qc_description,
            qc_replacement_value=qc_replacement_value
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

        init_location_site_name = location_data.get('site_name')
        init_location_name = location_data.get('location_name')
        init_location_latitude = location_data.get('location_latitude')
        init_location_longitude = location_data.get('location_longitude')
        init_location_description = location_data.get('location_description')

        init_location_form = {
            'site_name' : init_location_site_name,
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
        if not temp_site_location:

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
        'site_name' : site_name,
        'location_name' : location_name,
        'form' : form
    }

    return render(request, template, context)

def delete_location(request):

    params = request.GET
    site_name = params.get('site_name', '')
    location_name = params.get('location_name', '')

    Locations_by_site(site=site_name, location=location_name).delete()
    Location_info_by_location(location=location_name).delete()

    url = reverse('sites:index')

    return HttpResponseRedirect(url)

def manage_sensor(request):

    params = request.GET

    site_name = params.get('site_name', '')
    location_name = params.get('location_name', '')
    sensor_name = params.get('sensor_name', '')

    init_sensor_form = dict
    init_sensor_last_update = None
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




