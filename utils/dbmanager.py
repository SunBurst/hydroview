import os
import configparser
import logging
from collections import OrderedDict
from cassandra.cluster import Cluster, RetryPolicy
import cassandra.concurrent
from cassandra.query import BatchStatement

"""
	Script for retrieving/inserting records stored in the database.
"""

get_location_info_query = None
get_sensor_names_query = None
get_sensor_status_query = None
get_readings_query = None
get_battery_volt_query = None
add_reading_query = None
add_sensor_status_query = None
batch_add_readings_query = None

cfg = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, 'cfg', 'config.INI')

config_parser = configparser.ConfigParser()
try:
    config_parser.read(cfg)
except:
    print("could not load config file!")

host = [config_parser.get('DBSETTINGS', 'host')]
keyspace = config_parser.get('DBSETTINGS', 'keyspace')

log = logging.getLogger()
log.setLevel('INFO')
cluster = Cluster(
  contact_points=host,
   default_retry_policy = RetryPolicy()
  )

session = cluster.connect()
metadata = cluster.metadata
log.info("Connected to " +  metadata.cluster_name)
print("Connected to " +  metadata.cluster_name)
session.set_keyspace(keyspace)
session.default_timeout = 300.0

def cluster_disconnect():
    cluster.shutdown()

# API FOR QUERING

def get_location_info_by_locations():
    """
		
	"""
    global get_location_info_query
    if get_location_info_query is None:
	    get_location_info_query = session.prepare("""
            SELECT * FROM sites WHERE bucket = 0
        """)
    rows = session.execute(get_location_info_query)
    result = []
    for row in rows:
        result.append(row)
    return result

def get_sensor_names_by_location(location):
    global get_sensor_names_query
    if get_sensor_names_query is None:
        get_sensor_names_query = session.prepare("""
            SELECT * FROM sensors_by_location WHERE location = ?;
		""")
    rows = session.execute(get_sensor_names_query, (location,))
    result = []
    for row in rows:
        result.append(row)
    return result

def get_sensor_status_by_location(location):
    global get_sensor_status_query
    if get_sensor_status_query is None:
        get_sensor_status_query = session.prepare("""
           SELECT * FROM sensor_status_by_location WHERE location = ?	 
        """)
    rows = session.execute(get_sensor_status_query, (location,))
    return rows[0]	

#def get_readings_by_sensor_range(sensor, parameter, from_time, to_time):
#    get_readings_query = session.prepare("""
#        SELECT * FROM readings_by_sensor 
#        WHERE sensor = ? AND parameter = ? 
#        AND time >= ?
#        AND time < ?
#        """)
#    params = [(get_readings_query, (sensor, parameter, from_time, to_time,))]

#    results = cassandra.concurrent.execute_concurrent(session, params, raise_on_first_error=False)
#    for (success, result) in results:
#        if not success:
#            print(result)  # result will be an Exception
#        else:
#            print(result[0])
    #print(results[0].result())
    #future = session.execute_async(get_readings_query, (sensor, parameter, from_time, to_time))
    #result = []
    
    #try:
    #    rows = results.result()
    #    for row in rows:
    #        result.append(row)
    #    if not rows:
    #        print("No rows matching query!")
    #except NoHostAvailableException:
    #    print("No host available..")
    #print(results)
    #return results

def get_readings_by_sensor_range(params):
    if params: 
        get_readings_query = session.prepare("""
            SELECT * FROM readings_by_sensor 
            WHERE sensor = ? AND parameter = ? 
            AND time >= ?
            AND time < ?
            """)
    
        parameters = []
        result = []
	
        for row in params:
            (sensor, parameter, from_time, to_time) = row
            parameters.append((sensor,parameter,from_time,to_time,))

        try:
            results = cassandra.concurrent.execute_concurrent_with_args(session, get_readings_query, parameters, concurrency=50)
            for part in results:
                for row in part[1]:
                    result.append(row)
        except:
            print("Get sites query failed!")

        return result
    else:
        return []

    #print(results[0].result())
    #future = session.execute_async(get_readings_query, (sensor, parameter, from_time, to_time))
    #result = []
    
    #try:
    #    rows = results.result()
    #    for row in rows:
    #        result.append(row)
    #    if not rows:
    #        print("No rows matching query!")
    #except NoHostAvailableException:
    #    print("No host available..")
    #print(results)

def get_readings_by_sensor_time(sensor, parameter, time):
    global get_readings_query
    if get_readings_query is None:
        get_readings_query = session.prepare("""
            SELECT * FROM readings_by_sensor 
            WHERE sensor = ? AND parameter = ? 
            AND time = ?
            """)
        rows = session.execute(get_readings_query, (sensor, parameter, time))
        result = []
        for row in rows:
            result.append(row)
        if not rows:
            print("No rows matching query!")
        
        get_readings_query = None
        return result

def get_readings_by_sensor_asc(sensor, parameter, time):
    global get_readings_query
    if get_readings_query is None:
        get_readings_query = session.prepare("""
            SELECT * FROM readings_by_sensor 
            WHERE sensor = ? AND parameter = ? 
            AND time >= ?
            """)
        rows = session.execute(get_readings_query, (sensor, parameter, time))
        result = []
        for row in rows:
            result.append(row)
        if not rows:
            print("No rows matching query!")
        
        get_readings_query = None
        return result

def get_readings_by_sensor_desc(sensor, parameter, time):
    global get_readings_query
    if get_readings_query is None:
        get_readings_query = session.prepare("""
            SELECT * FROM readings_by_sensor 
            WHERE sensor = ? AND parameter = ? 
            AND time <= ?
            """)
        rows = session.execute(get_readings_query, (sensor, parameter, time))
        result = []
        for row in rows:
            result.append(row)
        if not rows:
            print("No rows matching query!")
        
        get_readings_query = None
        return result
		
def get_readings_by_sensor_all(sensor, parameter):
    global get_readings_query
    if get_readings_query is None:
        get_readings_query = session.prepare("""
            SELECT * FROM readings_by_sensor 
            WHERE sensor = ? AND parameter = ? 
			""")
        rows = session.execute(get_readings_query, (sensor, parameter))
        result = []
        for row in rows:
            result.append(row)
        if not rows:
            print("No rows matching query!")
        get_readings_query = None
        return result

def get_lastest_readings_by_sensor(sensor, parameter, to_time, limit):
    global get_readings_query
    if get_readings_query is None:
        get_readings_query = session.prepare("""
            SELECT * FROM readings_by_sensor 
            WHERE sensor = ? AND parameter = ? 
            AND time <= ?
            LIMIT ?
            """)
        rows = session.execute(get_readings_query, (sensor, parameter, to_time, limit))
        result = []
        for row in rows:
            result.append(row)
        if not rows:
            print("tomt!")
        print("LASTEST", result)
        get_readings_query = None

# API FOR INSERTION

#def store_reading(sensor, parameter, time, value):
#    global add_reading_query
#    if add_reading_query is None:
#        add_reading_query = session.prepare("""
#            INSERT INTO readings_by_sensor (sensor, parameter, time, value)
#            VALUES (?, ?, ?, ?)
#            """)
#        result = session.execute_async(add_reading_query, (sensor, parameter, time, value))
#        add_reading_query = None

def store_reading(values):
    add_reading_query = session.prepare("""
        INSERT INTO readings_by_sensor (sensor, parameter, time, value)
        VALUES (?, ?, ?, ?)
        """)
    parameters = []
    for row in values:
        (sensor, parameter, time, value) = row
        parameters.append((sensor, parameter, int(time), float(value),))
    #execute_concurrent_with_args(session, add_reading_query, parameters, concurrency=50)
    cassandra.concurrent.execute_concurrent_with_args(session, add_reading_query, parameters, concurrency=50)
    #futures = []
    #for row in values:
    #    (sensor, parameter, time, value) = row
    #    futures.append(session.execute_async(
    #        add_reading_query, (sensor, parameter, int(time), float(value),)))

    #for future in futures:
        #future.result()
    #return futures
    
#def store_sensor_status():
#    global add_sensor_status_query
#    if add_sensor_status_query is None:
#        add_sensor_status_query = session.execute("""
#        INSERT INTO sensor_status_by_location (location, battery_status, last_connected)
#        VALUES (?, ?, ?)
#		""")
		



#if __name__=='__main__':
	#get_row('wind_speed_1_by_day_lvl_0','island_hourly','2015-05-05')
	#get_row('wind_speed_1_by_day_lvl_0','island_hourly','2015-05-05',wind_speed_1=[5.0,6.0])
	#get_row('mean_water_temp_1_m_by_day_lvl_1','island_hourly','2015-05-05',event_time=['2015-05-04 05:00:00','2015-05-06 05:00:00'])
    #insert_from_file(r'C:\Users\Marcus\Desktop\Exjobb\Hydrogather\hydrogatherer\data\2014_Island_fixed_diag.dat')
    #test = get_location_info_by_locations()
    #test1 = get_sensor_names_by_location('Island')
    #test2 = get_sensor_status_by_location('Island')
    #get_readings_by_sensor('Island_hourly','humidity',1430802000000,1430805600000)
    #get_lastest_readings_by_sensor('Island_hourly','humidity',1430805600000,1)
    #store_reading('Island_hourly','humidity',1430805600000,106.2)
    #get_readings_by_sensor_all('Island_hourly','humidity')
    #print(test)
    #print(test1)
    #print(test2)
    #cluster.shutdown()