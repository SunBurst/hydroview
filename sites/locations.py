from .models import Locations_by_site, Location_info_by_location
from utils.tools import MiscTools

class LocationData(object):
    """Helper class for getting location related data from the Cassandra database. """

    @classmethod
    def get_all_locations(cls, site_id, location_name=None, json_request=None):
        """
        Return all locations belonging to a specific site, or the location with a specific name (if given).
        Return an empty list if not found.

        Keyword arguments:
        site_id -- site identifier (UUID)
        location_name -- name of location (str)
        json_request -- if true, convert uuid to string representation (bool).
        """
        locations_data = []
        all_locations_query = Locations_by_site.objects.filter(site_id=site_id)
        if location_name:
            all_locations_query = all_locations_query.filter(location_name=location_name)
        for row in all_locations_query:
            if json_request:
                location_id = MiscTools.uuid_to_str(row.location_id)
            else:
                location_id = row.location_id
            location = {
                'location_name' : row.location_name,
                'location_id' : location_id,
                'location_description' : row.location_description,
                'location_latitude' : row.location_position.get('location_latitude'),
                'location_longitude' : row.location_position.get('location_longitude')
            }
            locations_data.append(location)
        return locations_data

    @classmethod
    def get_location(cls, location_id):
        """
        Return location or an empty list if not found.

        Keyword arguments:
        location_id -- location identifier (UUID)
        """
        location_data = []
        location_query = Location_info_by_location.objects.filter(location_id=location_id)
        for row in location_query:
            location = {
                'location_name' : row.location_name,
                'location_description' : row.location_description,
                'location_latitude' : row.location_position.get('location_latitude'),
                'location_longitude' : row.location_position.get('location_longitude')
            }
            location_data.append(location)
        return location_data