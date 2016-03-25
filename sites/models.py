from cassandra.cqlengine import columns, models

from utils import tools
# Create your models here.

class Sites(models.Model):
    bucket = columns.Integer(primary_key=True, default=0)
    site_id = columns.UUID(primary_key=True)
    site_name = columns.Text(primary_key=True, clustering_order="ASC")
    site_description = columns.Text(default=None)
    site_position = columns.Map(columns.Text, columns.Float, default=None)

    @classmethod
    def get_all_sites(cls, json_request=None):
        """Return all sites or an empty list if not found.

        Keyword arguments:
        json_request -- if true, convert uuid to string representation (bool).
        """
        sites_data = []
        all_sites_query = cls.objects.filter(bucket=0)
        for row in all_sites_query:
            if json_request:
                site_id = tools.MiscTools.uuid_to_str(row.site_id)
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

class Site_info_by_site(models.Model):
    site_id = columns.UUID(primary_key=True)
    site_name = columns.Text()
    site_description = columns.Text(default=None)
    site_position = columns.Map(columns.Text, columns.Float, default=None)

    @classmethod
    def get_site(cls, site_id):
        """
        Return site or an empty list if not found.

        Keyword arguments:
        site_id -- site identifier (UUID)
        """
        site_data = []
        site_query = cls.objects.filter(site_id=site_id)
        for row in site_query:
            site = {
                'site_name' : row.site_name,
                'site_description' : row.site_description,
                'site_latitude' : row.site_position.get('site_latitude'),
                'site_longitude' : row.site_position.get('site_longitude'),
            }
            site_data.append(site)
        return site_data