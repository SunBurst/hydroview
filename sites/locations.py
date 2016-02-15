from .models import Locations_by_site, Location_info_by_location

class LocationsData(object):

    @classmethod
    def get_site_locations(cls, site_name):

        site_locations_data = []
        all_locations = Locations_by_site.objects.filter(site=site_name)

        for location in all_locations:
            temp_location = {'site' : location.site,
                             'location' : location.location}
            site_locations_data.append(temp_location)

        return site_locations_data

    @classmethod
    def get_location(cls, location_name):

        location_data = []
        location_info = Location_info_by_location.objects.filter(location=location_name)

        for location in location_info:
            temp_location = {'location' : location.location,
                                'description' : location.description,
                                'latitude' : location.latitude,
                                'longitude' : location.longitude}
            location_data.append(temp_location)

        return location_data