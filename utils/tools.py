import os
import configparser
from collections import OrderedDict

from settings.settings import CONFIG_PATH

class MiscTools(object):
    """Miscellaneous helper tools for formatting data. """

    @classmethod
    def get_init_time_formats(cls):
        LOGGER_TIME_FORMATS = OrderedDict()
        parser = configparser.ConfigParser()
        parser.read(os.path.join(CONFIG_PATH, 'loggertypes.INI'))
        for section in parser.sections():
            for key, val in parser.items(section):
                LOGGER_TIME_FORMATS[key] = val.split(',')

    @classmethod
    def uuid_to_str(cls, target_uuid):
        """Return string representation of a UUID."""
        return str(target_uuid)