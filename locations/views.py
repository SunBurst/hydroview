import json
import uuid
#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, render
from django.core.urlresolvers import reverse

from .forms import ManageLocationForm
from .models import Locations_by_site, Location_info_by_location
from sites.models import Site_info_by_site
from utils.tools import MiscTools

def location_info(request):
    params = request.GET
    site_id = params.get('site_id', '')
    location_id = params.get('location_id', '')
    template = 'locations/location_info.html'

    site_data = Site_info_by_site.get_site(site_id)
    location_data = Location_info_by_location.get_location(location_id)
    if site_data and location_data:
        site_map = site_data[0]
        location_map = location_data[0]

        site_name = site_map.get('site_name')
        location_name = location_map.get('location_name')
        location_description = location_map.get('location_description')
        location_latitude = location_map.get('location_latitude')
        location_longitude = location_map.get('location_longitude')


        context = {
            'site_name' : site_name,
            'location_name' : location_name,
            'location_description': location_description,
            'location_latitude' : location_latitude,
            'location_longitude' : location_longitude
        }
        return render(request, template, context)

def load_site_locations_json(request):
    params = request.GET
    site_id = params.get('site_id', '')
    location_name = params.get('location_name')
    json_request = params.get('json_request', '')
    locations_data = Locations_by_site.get_all_locations(site_id, location_name, json_request)
    return HttpResponse(json.dumps(locations_data), content_type='application/json')

def manage_location(request):
    params = request.GET
    site_id = params.get('site_id', '')
    site_name = params.get('site_name', '')
    init_site_id_name = site_name + ": " + site_id
    location_id = params.get('location_id', '')
    location_name = params.get('location_name', '')
    init_location_form = dict
    template = 'locations/manage_location.html'

    if location_id:    #: Edit existing location
        location_data = Locations_by_site.get_location(location_id)
        if location_data:
            location_map = location_data[0]
            init_location_name = location_data.get('location_name')
            init_location_latitude = location_data.get('location_latitude')
            init_location_longitude = location_data.get('location_longitude')
            init_location_description = location_data.get('location_description')
            init_location_form = {
                'site' : init_site_id_name,
                'location_id' : location_id,
                'location_name' : init_location_name,
                'location_latitude' : init_location_latitude,
                'location_longitude' : init_location_longitude,
                'location_description' : init_location_description
            }
        else:
            print("Couldn't load site info from database!")
    else:   #: Add new location
        init_location_form = {'site' : init_site_id_name}

    form = ManageLocationForm(request.POST or None, initial=init_location_form)

    if form.is_valid():
        location_name = form.cleaned_data['location_name']
        location_description = form.cleaned_data['location_description']
        location_position = form.clean_gps_coordinates()
        if not location_id:
            location_id = uuid.uuid4()
        else:
            try:
                Locations_by_site(site_id=site_id, location_name=location_name).delete()
                Location_info_by_location(location_id=location_id).delete()
            except:
                print("Delete location query failed!")
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

        url = reverse('locations:location_info')
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