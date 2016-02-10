from .models import Sites, Locations_by_site, Location_info_by_location

class SiteData(object):

    @classmethod
    def get_all_sites(cls):
        sites_data = []
        all_sites = Sites.objects.filter(bucket=0)

        for site in all_sites:

            current_site = {'site' : site.site,
                            'description' : site.description,
                            'latitude' : site.latitude,
                            'longitude' : site.longitude}
            sites_data.append(current_site)
        print(sites_data)
        return sites_data

    @classmethod
    def get_site_locations(cls, site_name):
        site_locations_data = []
        all_locations = Locations_by_site.objects.filter(site=site_name)

        for location in all_locations:
            current_location = {'site' : location.site,
                                'location' : location.location}
            site_locations_data.append(current_location)
        print(site_locations_data)

        return site_locations_data

    @classmethod
    def get_location(cls, location_name):
        location_data = []
        location_info = Location_info_by_location.objects.filter(location=location_name)
        for location in location_info:
            current_location = {'location' : location.location,
                                'description' : location.description,
                                'latitude' : location.latitude,
                                'longitude' : location.longitude}
            location_data.append(current_location)

        return location_data



