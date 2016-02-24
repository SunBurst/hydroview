from .models import Sites, Site_info_by_site

class SiteData(object):

    @classmethod
    def get_all_sites(cls):

        sites_data = []
        all_sites = Sites.objects.filter(bucket=0)

        for site in all_sites:

            temp_site = {'site' : site.site,
                         'description' : site.description,
                         'latitude' : site.position.get('latitude'),
                         'longitude' : site.position.get('longitude')}
            sites_data.append(temp_site)

        return sites_data

    @classmethod
    def get_site(cls, site_name):

        site_data = []
        site_info = Site_info_by_site.objects.filter(site=site_name)

        for site in site_info:

            temp_site = {'site' : site.site,
                         'description' : site.description,
                         'latitude' : site.position.get('latitude'),
                         'longitude' : site.position.get('longitude')}
            site_data.append(temp_site)

        return site_data




