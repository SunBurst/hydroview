import os, configparser, logging, time

from django.core.management.base import BaseCommand, CommandError

from cqlengine import connection
from cqlengine.management import sync_table

from sites.models import Locations, Readings_by_sensor
import utils.raw_queries as raw_queries
from . import raw_data_handler


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        """ Performs a full update including fixing floating points, 
            splitting the raw files into parameter files and stores 
            the values into the Cassandra database. """

        cfg_ids = ('cfg/identifiers.INI')
        cfg_dbinfo = ('cfg/config.INI')
        #cfg = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, 'cfg', 'identifiers.INI')
        parser_ids = configparser.ConfigParser()
        parser_dbinfo = configparser.ConfigParser()
        parser_ids.read(cfg_ids)
        parser_dbinfo.read(cfg_dbinfo)
        #sites = db.get_location_info_by_locations()
        
        host = [(parser_dbinfo.get('DBSETTINGS', 'host'))]
        keyspace = parser_dbinfo.get('DBSETTINGS', 'keyspace')
        
        logging.basicConfig(level=logging.INFO)
        connection.setup(host, keyspace)
        cluster = connection.get_cluster()
        session = cluster.connect()
        session.set_keyspace(keyspace)
        logging.info('Connected to "%s" database' % keyspace)
        
        sync_table(Locations)
        sync_table(Readings_by_sensor)

        locations = Locations.objects.filter(bucket=0)
    
        for location in locations:
            target_location = location.name    #: Get location name from query set.
            
            try:
                file_path = parser_ids.get('FILE_PATHS', target_location)

                if file_path:
                    num_new_readings, new_rows = raw_data_handler.update_files(target_location, file_path)

                    if new_rows:
                        #print("Beginning database insertion..")
                        try:
                            raw_queries.store_readings_concurrently(session, new_rows)
                            #self.store_readings(session, cluster, new_rows)
                        #for param, sites in new_rows.items():
                            #batch = []
                            #for i, row in enumerate(sites):
                                #try:
                                    #print(row[0], row[1], row[2], row[3])
                                    #Readings_by_sensor.create(sensor=row[0], parameter=row[1], time=row[2], value=row[3])
                                #except:
                                    #print("Query timed out..")
                                    #cluster.shutdown()
                                #batch.append(row)
                            #db.store_reading(batch)
                        except:
                            logging.info('Query timed out! Shutting down session..')     
                            cluster.shutdown()
                        logging.info('Successfully inserted "%s" new sites!' % num_new_readings)
                        #self.stdout.write(self.style.SUCCESS('Successfully inserted "%s" new sites!' % num_new_readings))
                else:
                    raise CommandError('No file path set for location "%s"!' % target_location)
            except KeyError:
                raise CommandError('Location "%s" not configured' % target_location)