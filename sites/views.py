import json
import uuid
#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, HttpResponse, redirect, render
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta

from .charts import ChartData
from .forms import ManageSiteForm
from .models import Sites, Site_info_by_site
from locations.models import Locations_by_site

def index(request):
    template_name = 'sites/index.html'
    context = {}
    return render(request, template_name, context)

def settings(request):
    template_name = 'sites/settings.html'
    context = {}
    return render(request, template_name, context)

def site_info(request):
    params = request.GET
    site_id = params.get('site_id', '')
    template = 'sites/site_info.html'

    site_data = Site_info_by_site.get_site(site_id)

    if site_data:
        site_map = site_data[0]
        site_name = site_map.get('site_name')
        site_description = site_map.get('site_description')
        site_latitude = site_map.get('site_latitude')
        site_longitude = site_map.get('site_longitude')

        context = {
            'site_name' : site_name,
            'site_description' : site_description,
            'site_latitude' : site_latitude,
            'site_longitude' : site_longitude
        }
        return render(request, template, context)

def load_all_sites_json(request):
    params = request.GET
    json_request = params.get('json_request', '')
    sites_data = Sites.get_all_sites(json_request)
    return HttpResponse(json.dumps(sites_data), content_type='application/json')

def manage_site(request):
    params = request.GET
    site_id = params.get('site_id', '')
    site_name = params.get('site_name', '')
    init_site_form = dict
    template = 'sites/manage_site.html'

    if site_id:    #: Edit existing site
        site_data = Site_info_by_site.get_site(site_id)
        if site_data:
            site_map = site_data[0]
            init_site_name = site_map.get('site_name')
            init_site_description = site_map.get('site_description')
            init_site_latitude = site_map.get('site_latitude')
            init_site_longitude = site_map.get('site_longitude')
            init_site_form = {
            'site_id' : site_id,
            'site_name' : init_site_name,
            'site_description' : init_site_description,
            'site_latitude' : init_site_latitude,
            'site_longitude' : init_site_longitude
        }
        else:
            print("Couldn't load site info from database!")

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
            try:
                Sites(bucket=0, site_id=site_id).delete()
                Site_info_by_site(site_id=site_id).delete()
            except:
                print("Delete site query failed!")
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




