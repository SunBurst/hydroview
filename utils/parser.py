import os
from configparser import ConfigParser

from settings.base import CONFIG_PATH

class CustomParser(ConfigParser):

    def __init__(self, conf_filename):
        ConfigParser.__init__(self)
        self.conf_file = os.path.join(CONFIG_PATH, conf_filename)
        self.read(self.conf_file)

    def safe_set(self, section, option, value):
        if self.has_section(section):
            self.set(section, option, str(value))
        else:
            self.add_section(section)
            self.set(section, option, str(value))

    def safe_get(self, section, option):
        if self.has_option(section, option):
            return self.get(section, option)
        else:
            return None

class DatabaseSettingsParser(CustomParser):

    def __init__(self, db_conf_filename):
        CustomParser.__init__(self, db_conf_filename)

    def load_local_settings(self):
        self.cassandra_keyspace = self.safe_get('CONNECTION', 'keyspace')
        self.cassandra_host = self.safe_get('CONNECTION', 'host')
        self.cassandra_port = self.safe_get('CONNECTION', 'port')
        self.cassandra_class = self.safe_get('CONNECTION', 'class')
        self.cassandra_replication_factor = self.safe_get('CONNECTION', 'replication_factor')

    def load_production_settings(self):
        print("No yet supported!")