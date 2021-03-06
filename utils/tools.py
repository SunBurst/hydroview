import os
from collections import OrderedDict

from settings.base import CONFIG_PATH

class MiscTools(object):
    """Miscellaneous helper tools for formatting data. """

    @classmethod
    def uuid_to_str(cls, target_uuid):
        """Return string representation of a UUID."""
        return str(target_uuid)