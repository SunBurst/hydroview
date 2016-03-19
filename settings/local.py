from .base import *

from cassandra import ConsistencyLevel

from utils import parser

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(9)2w=5n11058$6n%s579wns@!_7lholaogzxgie0un6qij7o4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database

db_settings = parser.DatabaseSettingsParser('cassandra_config.ini')
db_settings.load_local_settings()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'cassandra': {
        'ENGINE': 'django_cassandra_engine',
        'NAME': db_settings.cassandra_keyspace,
        'TEST': {'NAME': 'test_db'},
        'HOST': db_settings.cassandra_host,
        'OPTIONS': {
            'replication': {
                'strategy_class': db_settings.cassandra_class,
                'replication_factor': db_settings.cassandra_replication_factor
            },
            'connection': {
                'consistency': ConsistencyLevel.ONE,
                'retry_connect': True
            },
            'session': {
                'default_timeout': 500,
                'default_fetch_size': 10000
            }
        }
    }
}