from cassandra.cluster import Cluster
from django.core.management.base import NoArgsCommand
import configparser

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        
        cfg = ('cfg/config.INI')
        config_parser = configparser.ConfigParser()
        try:
            config_parser.read(cfg)
        except:
            print("could not load config file!")
        
        host = [config_parser.get('DBSETTINGS', 'host')]
        keyspace = config_parser.get('DBSETTINGS', 'keyspace')
        cluster = Cluster(host)
        session = cluster.connect()

        rows = session.execute(
            "SELECT * FROM system.schema_keyspaces WHERE keyspace_name='%s'" % keyspace)

        if rows:
            msg = 'Keyspace "%s" already exists!\n'  % keyspace
            msg += 'Drop and recreate? All current data will '
            msg += 'be deleted! (y/n): '
            resp = input(msg)
            if not resp or resp[0] != 'y':
                print("Ok, then we're done here.")
                return
            session.execute("DROP KEYSPACE %s" % keyspace)

        strategy = config_parser.get('DBSETTINGS', 'class')
        rep_factor = config_parser.get('DBSETTINGS', 'replication_factor')
		
        session.execute("""
            CREATE KEYSPACE %s
            WITH replication = {'class': '%s', 'replication_factor': '%s'}
            """ % (keyspace, strategy, rep_factor))

        session.set_keyspace(keyspace)

        session.execute("""
            CREATE TABLE erken.sites (
                bucket int, 
                name text, 
                description text, 
                num_sensors int,
                latitude float, 
                longitude float, 
            PRIMARY KEY((bucket), name)
            ) WITH CLUSTERING ORDER BY (name ASC)
            """)

        session.execute("""
            CREATE TABLE erken.sensors_by_location (
                location text, 
                sensor text, 
                PRIMARY KEY((location), sensor)
                ) WITH CLUSTERING ORDER BY (sensor ASC)
            """)

        session.execute("""
            CREATE TABLE erken.readings_by_sensor (
                sensor text, 
                parameter text, 
                time timestamp, 
                value float,
                PRIMARY KEY((sensor, parameter), time)
                ) WITH CLUSTERING ORDER BY (time DESC)
            """)

        session.execute("""
            CREATE TABLE erken.sensor_status_by_location (
                location text, 
                last_connected timestamp, 
                battery_status text,
                PRIMARY KEY(location)
                )
            """)

        print('Keyspace "%s" created!' % keyspace)
