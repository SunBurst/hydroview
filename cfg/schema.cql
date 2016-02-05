/* Cassandra schema for Erken */

DROP KEYSPACE IF EXISTS erken;

/* The database is only running on a single cluster 
on a single node for the time being. */

CREATE KEYSPACE erken 
WITH REPLICATION = { 
	'class' : 'SimpleStrategy', 
	'replication_factor' : 1 
};

USE erken;

/* Table for storing information for each location with sensors 
connected to it. A bucket will store all locations into one 
single partition rather than one for each location. 
*/

CREATE TABLE erken.locations (
	bucket int, 
	name text, 
	description text, 
	num_sensors int,
	latitude float, 
	longitude float, 
	PRIMARY KEY((bucket), name)
) WITH CLUSTERING ORDER BY (name ASC);

/* Table for storing all sensors belonging to a specific location. */

CREATE TABLE erken.sensors_by_location (
	location text, 
	sensor text, 
	PRIMARY KEY((location), sensor)
) WITH CLUSTERING ORDER BY (sensor ASC);

/* Table for storing readings by all sensors, partitioned by
sensor and parameter. */

CREATE TABLE erken.readings_by_sensor (
	sensor text, 
	parameter text, 
	time timestamp, 
	value float,
	PRIMARY KEY((sensor, parameter), time)
) WITH CLUSTERING ORDER BY (time DESC);

/* Table for storing each location's sensor status. */

CREATE TABLE erken.sensor_status_by_location (
	location text, 
	last_connected timestamp, 
	battery_status text,
	PRIMARY KEY(location)
);