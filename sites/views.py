import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import HttpResponse, redirect, render
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta

from .charts import ChartData
from .forms import ManageLocationForm, ManageSensorForm, ManageSiteForm
from .locations import LocationData
from .sensors import SensorData
from .sites import SiteData
from .models import Locations_by_site, Location_info_by_location, Sensors_by_location, Sensor_info_by_sensor, Sites, Site_info_by_site


###########################################################################
######################    API FOR LOADING TEMPLATES    ####################
###########################################################################

def index(request):
    template_name = 'sites/index.html'
    #sites_data = SiteData.get_all_sites()
    #print(sites_data)
    #monitored_sites = []
    context = {}
    #context = {'monitored_sites' : []}
    #for site in sites_data:
    #    current_site = {
    #                'site' : site['site'],
     #               'description' : site['description'],
     #               'latitude' : site['latitude'],
     #               'longitude' : site['longitude']
    #        }
     #   monitored_sites.append(current_site)
    #context['monitored_sites'] = monitored_sites

    return render(request, template_name, context)

def load_location(request):

    params = request.GET

    site_name = params.get('site_name', '')
    location_name = params.get('location_name', '')

    template = 'sites/location.html'

    context = {}

    location_data_list = LocationData.get_location(location_name)
    location_data = location_data_list[0]

    init_site_name = site_name
    init_location_name = location_name
    init_location_description = location_data.get('description')
    init_location_latitude = location_data.get('latitude')
    init_location_longitude = location_data.get('longitude')

    initLocationForm = {'site' : init_site_name, 'location' : init_location_name, 'description' : init_location_description, 'latitude' : init_location_latitude, 'longitude' : init_location_longitude}

    context = {
                'site_name' : init_site_name,
                'location_name' : init_location_name,
                'description' : init_location_description,
                'longitude' : init_location_longitude,
                'latitude': init_location_latitude
    }

    form = ManageLocationForm(request.POST or None, initial=initLocationForm)
    context['form'] = form

    if form.is_valid():
        location_name = form.cleaned_data['location']
        location_description = form.cleaned_data['description']
        location_position = form.clean_gps_coordinates()

        Locations_by_site(site=init_site_name, location=init_location_name).delete()
        Location_info_by_location(location=init_location_name).delete()

        Locations_by_site.create(
            site=site_name,
            location=location_name,
            description=location_description,
            position=location_position
        )

        Location_info_by_location.create(
            location=location_name,
            description=location_description,
            position=location_position
        )

        url = reverse('sites:load_location')
        url += '?site_name=' + init_site_name + '&location_name=' + location_name

        return HttpResponseRedirect(url)

    return render(request, template, context)



###########################################################################
#####################    API FOR RETURNING JSON DATA    ###################
###########################################################################

def date_handler(dt):
    return dt.isoformat() if hasattr(dt, 'isoformat') else dt

def load_sites_json(request):

    sites_data = SiteData.get_all_sites()
    return HttpResponse(json.dumps(sites_data), content_type='application/json')

def load_sensors_json(request):

    params = request.GET
    location_name = params.get('location_name', '')
    sensors_data = SensorData.get_sensors_by_location(location_name)
    location_sensors_data = []

    for sensor in sensors_data:
        sensor_name = sensor.get('sensor')
        sensor_info = SensorData.get_sensor(sensor_name)
        temp_sensor_dict = sensor_info[0]
        temp_last_update = date_handler(temp_sensor_dict.get('last_update'))
        temp_next_update = date_handler(temp_sensor_dict.get('next_update'))
        temp_sensor_dict['last_update'] = temp_last_update
        temp_sensor_dict['next_update'] = temp_next_update
        location_sensors_data.append(temp_sensor_dict)

    return HttpResponse(json.dumps(location_sensors_data), content_type='application/json')

def load_locations_json(request):

    params = request.GET
    site_name = params.get('site_name', '')
    locations_data = LocationData.get_site_locations(site_name)

    return HttpResponse(json.dumps(locations_data), content_type='application/json')

###########################################################################
#######################    API FOR MANAGING FORMS    ######################
###########################################################################

def manage_site(request):

    params = request.GET
    site_name = params.get('site_name', '')
    init_site_form = dict
    template = 'sites/manage_site.html'

    if site_name:    #: Edit existing site
        site_data_list = SiteData.get_site(site_name)
        site_data = site_data_list[0]

        init_site_name = site_data.get('site')
        init_site_description = site_data.get('description')
        init_site_latitude = site_data.get('latitude')
        init_site_longitude = site_data.get('longitude')

        init_site_form = {'site' : init_site_name, 'description' : init_site_description, 'latitude' : init_site_latitude, 'longitude' : init_site_longitude}

    else:   #: Add new site
        init_site_form = {}

    form = ManageSiteForm(request.POST or None, initial=init_site_form)

    if form.is_valid():
        site_name = form.cleaned_data['site']
        site_description = form.cleaned_data['description']
        site_position = form.clean_gps_coordinates()

        Sites.create(
            bucket=0,
            site=site_name,
            description=site_description,
            position = site_position
        )

        Site_info_by_site.create(
            site=site_name,
            description=site_description,
            position = site_position
        )

        url = reverse('sites:index')

        return HttpResponseRedirect(url)

    context = {
        'site_name' : site_name,
        'form' : form
    }

    return render(request, template, context)

def delete_site(request):

    params = request.GET
    site_name = params.get('site_name', '')

    Sites(bucket=0, site=site_name).delete()
    Site_info_by_site(site=site_name).delete()

    url = reverse('sites:index')

    return HttpResponseRedirect(url)

def manage_location(request):

    params = request.GET
    site_name = params.get('site_name', '')
    location_name = params.get('location_name', '')

    init_location_form = dict
    template = 'sites/manage_location.html'

    if location_name:    #: Edit existing location
        location_data_list = LocationData.get_location(location_name)
        location_data = location_data_list[0]

        init_location_site = site_name
        init_location_name = location_name
        init_location_latitude = location_data.get('latitude')
        init_location_longitude = location_data.get('longitude')
        init_location_description = location_data.get('description')

        init_location_form = {'site' : init_location_site, 'location' : init_location_name, 'latitude' : init_location_latitude, 'longitude' : init_location_longitude, 'description' : init_location_description}

    else:   #: Add new location
        init_location_form = {'site' : site_name}

    form = ManageLocationForm(request.POST or None, initial=init_location_form)

    if form.is_valid():
        site_name = form.cleaned_data['site']
        location_name = form.cleaned_data['location']
        location_description = form.cleaned_data['description']
        location_position = form.clean_gps_coordinates()

        Locations_by_site.create(
            site=site_name,
            location=location_name,
            description=location_description,
            position=location_position
        )

        Location_info_by_location.create(
            location=location_name,
            description=location_description,
            position=location_position
        )

        url = reverse('sites:load_location')
        url += '?site_name=' + site_name + '&location_name=' + location_name

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

        sensor_num = SensorData.get_sensor_num(location_name, sensor_name)
        sensor_data_list = SensorData.get_sensor(sensor_name)
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
    name = params.get('name', '')

    if name == 'humidity_by_day':
        data = ChartData.get_humidity_data_by_day(days=int(days))
            #user=request.user) #days=int(days))
    #elif name == 'avg_by_day':
    #    data['chart_data'] = ChartData.get_avg_by_day(
    #        user=request.user, days=int(days))
    #elif name == 'level_breakdown':
    #    data['chart_data'] = ChartData.get_level_breakdown(
    #        user=request.user, days=int(days))
    #elif name == 'count_by_category':
    #    data['chart_data'] = ChartData.get_count_by_category(
    #        user=request.user, days=int(days))
    #print(json.dumps(data))
    return HttpResponse(json.dumps(data), content_type='application/json')

    ###### HEEEEEY -> <div id="chart_panel" class="panel-body"
        #style="width:100%;height:314px"></div>




