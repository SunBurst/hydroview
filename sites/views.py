import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import HttpResponse, redirect, render
from django.views import generic

from .charts import ChartData
from .forms import ManageLocationForm, ManageSiteForm
from .sites import SiteData
from .models import Locations_by_site, Location_info_by_location, Sites, Site_info_by_site

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


def load_sites_data(request):
    print("HEJ", request)
    params = request.GET

    name = params.get('name', '')

    if name == 'load_all_sites':
        sites_data = SiteData.get_all_sites()
        print(json.dumps(sites_data))
        return HttpResponse(json.dumps(sites_data), content_type='application/json')
    return HttpResponse(json.dumps("test"), content_type='application/json')

def load_location(request):
    template_name = 'sites/location.html'
    params = request.GET

    site_name = params.get('site_name', '')
    location_name = params.get('location_name', '')

    location_info = Location_info_by_location.objects.filter(location=location_name)
    context = {}
    for location in location_info:
        context = {'site' : site_name,
                   'location' : location.location,
                   'description' : location.description,
                   'latitude' : location.latitude,
                   'longitude' : location.longitude}
    return render(request, template_name, context)

def load_location_data(request):
    params = request.GET
    location_data = []
    name = params.get('name', '')
    location = params.get('location', '')

    if name == 'load_location':
        location_data = SiteData.get_location(location)
        return HttpResponse(json.dumps(location_data), content_type='application/json')
    return HttpResponse(json.dumps(location_data), content_type='application/json')

def load_locations_data(request):
    print("HEJ LOCATIONS", request)
    params = request.GET

    name = params.get('name', '')
    site = params.get('site', '')

    if name == 'load_site':
        locations_data = SiteData.get_site_locations(site)
        print(site, json.dumps(locations_data))
        return HttpResponse(json.dumps(locations_data), content_type='application/json')
    return HttpResponse(json.dumps("test"), content_type='application/json')

def dashboard(request):#request, chartID = 'chart_ID', chart_type = 'line', chart_height = 400):
    template = 'sites/dashboard.html'
    #status_data = ChartData.get_status_data()
    #print(status_data)

    #chart = {"renderTo": chartID, "type": chart_type, "zoomType": 'x', "height": chart_height,}
    #title = {"text": 'Battery Status'}
    #xAxis = {"title": {"text": 'Time (Local)'}, "type": 'datetime'}
    #yAxis = {"title": {"text": 'Battery (V)'}}
    #series = status_data#[{
        #'name' : status_data['location'],
        #'data': test
        #}]

    #context = {'locations_list': sites}
    #render(request, template, context)
    #print(template, chartID, chart, series, title, xAxis, yAxis)
    #return render(request, template, {'chartID': chartID, 'chart': chart,
    #                                                'series': series, 'title': title,
    #                                                'xAxis': xAxis, 'yAxis': yAxis})
    return render(request, template)

def manage_site(request):

    params = request.GET
    site = params.get('site_name', '')

    site_fill_form = dict
    template = 'sites/manage_site.html'

    if site:    #: Edit existing site

        site_data = SiteData.get_site(site)
        site_info_dict = site_data[0]

        fill_site_name = site_info_dict.get('site')
        fill_site_desc = site_info_dict.get('description')
        fill_site_lat = site_info_dict.get('latitude')
        fill_site_long = site_info_dict.get('longitude')

        site_fill_form = {'site' : fill_site_name, 'description' : fill_site_desc, 'latitude' : fill_site_lat, 'longitude' : fill_site_long}

    else:   #: Add new site

        site_fill_form = {}
        template = 'sites/add_site.html'

    form = ManageSiteForm(request.POST or None, initial=site_fill_form)

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

        return HttpResponseRedirect('/sites/')

    context = {
        'form' : form
    }

    return render(request, template, context)

def manage_location(request):

    params = request.GET
    site = params.get('site_name', '')
    location = params.get('location_name', '')

    location_fill_form = dict
    template = 'sites/manage_location.html'

    if location:    #: Edit existing location
        pass
    else:   #: Add new location
        location_fill_form = {'site' : site}
        template = 'sites/add_location.html'

    form = ManageLocationForm(request.POST or None, initial=location_fill_form)

    if form.is_valid():
        site_name = form.cleaned_data['site']
        location_name = form.cleaned_data['location']
        location_description = form.cleaned_data['description']
        location_latitude = form.cleaned_data['latitude']
        location_longitude = form.cleaned_data['longitude']

        Locations_by_site.create(
            site=site_name,
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

        return HttpResponseRedirect('/sites/')

    context = {
        'form' : form
    }

    return render(request, template, context)

def chart_data_json(request):

    params = request.GET

    days = params.get('days', 0)
    name = params.get('name', '')

    if name == 'status_by_day':
        data = ChartData.get_status_data_by_day(days=int(days))
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




