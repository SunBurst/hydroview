import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import HttpResponse, redirect, render
from django.core.urlresolvers import reverse

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
    template_name = 'sites/location.html'
    params = request.GET

    siteName = params.get('site_name', '')
    locationName = params.get('location_name', '')

    context = {}

    locationDataList = LocationData.get_location(locationName)
    locationData = locationDataList[0]

    initSiteName = siteName
    initLocationName = locationName
    initLocationLat = locationData.get('latitude')
    initLocationLong = locationData.get('longitude')
    initLocationDesc = locationData.get('description')

    initLocationForm = {'site' : initSiteName, 'location' : initLocationName, 'latitude' : initLocationLat, 'longitude' : initLocationLong, 'description' : initLocationDesc}

    context = {
                'site_name' : initSiteName,
                'location_name' : initLocationName,
                'longitude' : initLocationLong,
                'latitude': initLocationLat,
                'description' : initLocationDesc
    }
    #for location in location_info:
    #    location_fill_form = {
    #                            'site' : site_name,
    #                            'location' : location.location,
    #                            'description' : location.description,
    #                            'latitude' : location.latitude,
    #                            'longitude' : location.longitude
    #    }
    #    context = {
    #                'site' : site_name,
    #                'location' : location.location,
    #                'description' : location.description,
    #                'latitude' : location.latitude,
    #                'longitude' : location.longitude
    #    }

    form = ManageLocationForm(request.POST or None, initial=initLocationForm)
    context['form'] = form

    if form.is_valid():
        #site_name = form.cleaned_data['site']
        newLocationName = form.cleaned_data['location']
        newLocationDesc = form.cleaned_data['description']
        newLocationLat = form.cleaned_data['latitude']
        newLocationLong = form.cleaned_data['longitude']

        Locations_by_site(site=initSiteName, location=initLocationName).delete()
        Location_info_by_location(location=initLocationName).delete()

        Locations_by_site.create(
            site=initSiteName,
            location=newLocationName,
            latitude = newLocationLat,
            longitude = newLocationLong,
            description=newLocationDesc
        )

        Location_info_by_location.create(
            location=newLocationName,
            latitude = newLocationLat,
            longitude = newLocationLong,
            description=newLocationDesc
        )

        url = reverse('sites:load_location')
        url += '?site_name=' + initSiteName + '&location_name=' + newLocationName

        return HttpResponseRedirect(url)

    return render(request, template_name, context)



###########################################################################
#####################    API FOR RETURNING JSON DATA    ###################
###########################################################################

def load_sites_json(request):

    sites_data = SiteData.get_all_sites()
    return HttpResponse(json.dumps(sites_data), content_type='application/json')

def load_sensors_json(request):
    params = request.GET

    site_name = params.get('site_name', '')
    location_name = params.get('location_name', '')

    sensors = SensorData.get_sensors_by_location(location_name)

    location_sensors = []

    for sensor in sensors:
        sensor_name = sensor.get('sensor')

        sensor_info = SensorData.get_sensor(sensor_name)

        temp_sensor_dict = sensor_info[0]

        location_sensors.append(temp_sensor_dict)

    return HttpResponse(json.dumps(location_sensors), content_type='application/json')

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
    site = params.get('site_name', '')
    initSiteForm = dict
    template = 'sites/manage_site.html'

    if site:    #: Edit existing site

        site_data = SiteData.get_site(site)
        site_info_dict = site_data[0]

        fill_site_name = site_info_dict.get('site')
        fill_site_desc = site_info_dict.get('description')
        fill_site_lat = site_info_dict.get('latitude')
        fill_site_long = site_info_dict.get('longitude')

        initSiteForm = {'site' : fill_site_name, 'description' : fill_site_desc, 'latitude' : fill_site_lat, 'longitude' : fill_site_long}

    else:   #: Add new site

        initSiteForm = {}

    form = ManageSiteForm(request.POST or None, initial=initSiteForm)

    if form.is_valid():
        site_name = form.cleaned_data['site']
        site_description = form.cleaned_data['description']
        site_latitude = form.cleaned_data['latitude']
        site_longitude = form.cleaned_data['longitude']

        Sites.create(
            bucket=0,
            site=site_name,
            description=site_description,
            latitude = site_latitude,
            longitude = site_longitude
        )

        Site_info_by_site.create(
            site=site_name,
            description=site_description,
            latitude = site_latitude,
            longitude = site_longitude
        )

        url = reverse('sites:index')

        return HttpResponseRedirect(url)

    context = {
        'site_name' : site,
        'form' : form
    }

    return render(request, template, context)

def delete_site(request):

    params = request.GET
    siteName = params.get('site_name', '')

    Sites(bucket=0, site=siteName).delete()
    Site_info_by_site(site=siteName).delete()

    url = reverse('sites:index')

    return HttpResponseRedirect(url)



def manage_location(request):

    params = request.GET
    siteName = params.get('site_name', '')
    locationName = params.get('location_name', '')

    initLocationForm = dict
    template = 'sites/manage_location.html'

    if locationName:    #: Edit existing location
        locationDataList = LocationData.get_location(locationName)
        locationData = locationDataList[0]

        initLocationSite = siteName
        initLocationName = locationName
        initLocationLat = locationData.get('latitude')
        initLocationLong = locationData.get('longitude')
        initLocationDesc = locationData.get('description')

        initLocationForm = {'site' : initLocationSite, 'location' : initLocationName, 'latitude' : initLocationLat, 'longitude' : initLocationLong, 'description' : initLocationDesc}

    else:   #: Add new location
        initLocationForm = {'site' : siteName}

    form = ManageLocationForm(request.POST or None, initial=initLocationForm)

    if form.is_valid():
        site_name = form.cleaned_data['site']
        location_name = form.cleaned_data['location']
        location_description = form.cleaned_data['description']
        location_latitude = form.cleaned_data['latitude']
        location_longitude = form.cleaned_data['longitude']

        Locations_by_site.create(
            site=siteName,
            location=location_name,
            description=location_description,
            latitude = location_latitude,
            longitude = location_longitude
        )

        Location_info_by_location.create(
            location=location_name,
            description=location_description,
            latitude = location_latitude,
            longitude = location_longitude
        )

        url = reverse('sites:load_location')
        url += '?site_name=' + siteName + '&location_name=' + location_name

        return HttpResponseRedirect(url)

    context = {
        'site_name' : siteName,
        'location_name' : locationName,
        'form' : form
    }

    return render(request, template, context)

def delete_location(request):

    params = request.GET
    siteName = params.get('site_name', '')
    locationName = params.get('location_name', '')

    Locations_by_site(site=siteName, location=locationName).delete()
    Location_info_by_location(location=locationName).delete()

    url = reverse('sites:index')

    return HttpResponseRedirect(url)

def manage_sensor(request):
    params = request.GET

    siteName = params.get('site_name', '')
    locationName = params.get('location_name', '')
    sensorName = params.get('sensor_name', '')

    initSensorForm = dict

    template = 'sites/manage_sensor.html'

    if sensorName:    #: Edit existing sensor

        sensorNum = SensorData.get_sensor_num(locationName, sensorName)

        sensorDataList = SensorData.get_sensor(sensorName)
        sensorData = sensorDataList[0]

        initSensorLocation = locationName
        initSensorNum = sensorNum
        initSensorName = sensorData.get('sensor')
        initSensorDesc = sensorData.get('description')
        initSensorFilePath = sensorData.get('file_path')
        initSensorFileLineNum = sensorData.get('file_line_num')
        initSensorTimeFormat = sensorData.get('time_format')
        initSensorTimeZone = sensorData.get('time_zone')
        initSensorParamsList = sensorData.get('parameters')
        initSensorParams = ",".join(initSensorParamsList)
        initSensorTimeIds = sensorData.get('time_ids')

        initSensorForm = {'location' : initSensorLocation, 'sensor_num' : initSensorNum, 'sensor' : initSensorName, 'description' : initSensorDesc, 'file_path' : initSensorFilePath, 'file_line_num' : initSensorFileLineNum, 'time_format' : initSensorTimeFormat, 'time_zone' : initSensorTimeZone, 'time_ids' : initSensorTimeIds, 'parameters' : initSensorParams}

    else:   #: Add new sensor
        initSensorForm = {'location' : locationName}

    form = ManageSensorForm(request.POST or None, initial=initSensorForm)

    if form.is_valid():
        sensorNum = form.cleaned_data['sensor_num']
        sensorName = form.cleaned_data['sensor']
        sensorDesc = form.cleaned_data['description']
        sensorLineNum = form.cleaned_data['file_line_num']
        sensorFilePath = form.cleaned_data['file_path']
        sensorTimeFormat = form.cleaned_data['time_format']
        sensorTimeZone = form.cleaned_data['time_zone']
        sensorTimeIds = form.cleanTimeIds(sensorTimeFormat)
        sensorParams = form.cleaned_data['parameters'].split(',')
        sensorTimeInfo = {'time_format' : sensorTimeFormat,
                          'time_zone' : sensorTimeZone,
                          'time_ids' : sensorTimeIds
        }

        Sensors_by_location.create(
            location=locationName,
            sensor=sensorName,
            sensor_num=sensorNum,
            description=sensorDesc
        )

        Sensor_info_by_sensor.create(
            sensor=sensorName,
            description=sensorDesc,
            file_path=sensorFilePath,
            file_line_num=sensorLineNum,
            parameters=sensorParams,
            time_info=sensorTimeInfo,
        )

        url = reverse('sites:load_location')
        url += '?site_name=' + siteName + '&location_name=' + locationName

        return HttpResponseRedirect(url)

    context = {
        'site_name' : siteName,
        'location_name' : locationName,
        'form' : form
    }

    return render(request, template, context)

def delete_sensor(request):
    params = request.GET

    siteName = params.get('site_name', '')
    locationName = params.get('location_name', '')
    sensorName = params.get('sensor_name', '')

    Sensors_by_location(location=locationName).delete()
    Sensor_info_by_sensor(sensor=sensorName).delete()

    url = reverse('sites:load_location')
    url += '?site_name=' + siteName + '&location_name=' + locationName

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




