
"""
Store object's element key data in memory.
"""

from django.conf import settings
from muddery.server.utils import utils


class SystemData(object):
    """
    The storage of system data.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    storage = storage_class("system_data", "", "")

    @classmethod
    def save(cls, key, value):
        """
        Store a value.
        :return:
        """
        cls.storage.save("", "", {
            key: value
        })

    @classmethod
    def load(cls, key, *default):
        """
        Load a value.
        :return:
        """
        try:
            data = cls.storage.load("", "")
            return data[key]
        except KeyError as e:
            if len(default) > 0:
                return default[0]
            else:
                raise e
