from .models import Sites, Site_info_by_site
from utils.tools import MiscTools

class SiteData(object):
    """Helper class for getting site related data from the Cassandra database. """

    @classmethod
    def get_all_sites(cls, json_request=None):
        """Return all sites or an empty list if not found.

        Keyword arguments:
        json_request -- if true, convert uuid to string representation (bool).
        """
        sites_data = []
        all_sites_query = Sites.objects.filter(bucket=0)
        for row in all_sites_query:
            if json_request:
                site_id = MiscTools.uuid_to_str(row.site_id)
            else:
                site_id = row.site_id
            site = {
                'site_id' : site_id,
                'site_name' : row.site_name,
                'site_description' : row.site_description,
                'site_latitude' : row.site_position.get('site_latitude'),
                'site_longitude' : row.site_position.get('site_longitude')
            }
            sites_data.append(site)
        return sites_data

    @classmethod
    def get_site(cls, site_id):
        """
        Return site or an empty list if not found.

        Keyword arguments:
        site_id -- site identifier (UUID)
        """
        site_data = []
        site_query = Site_info_by_site.objects.filter(site_id=site_id)
        for row in site_query:
            site = {
                'site_name' : row.site_name,
                'site_description' : row.site_description,
                'site_latitude' : row.site_position.get('site_latitude'),
                'site_longitude' : row.site_position.get('site_longitude')
            }
            site_data.append(site)
        return site_data




