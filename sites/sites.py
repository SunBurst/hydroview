from .models import Sites, Site_info_by_site

class SiteData(object):
    """Helper class for getting site related data from the Cassandra database. """

    @classmethod
    def get_all_sites(cls):
        """Return all sites or an empty list if not found. """
        sites_data = []
        all_sites_query = Sites.objects.filter(bucket=0)
        for row in all_sites_query:
            site = {
                'site_id' : row.site_id,
                'site_name' : row.site_name,
                'description' : row.description,
                'latitude' : row.position.latitude,
                'longitude' : row.position.longitude
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
                'description' : row.description,
                'latitude' : row.position.latitude,
                'longitude' : row.position.longitude
            }
            site_data.append(site)
        return site_data




