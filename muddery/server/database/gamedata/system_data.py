
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class SystemData(BaseData, Singleton):
    """
    The storage of system data.
    """
    __table_name = "system_data"
    __category_name = ""
    __key_field = ""
    __default_value_field = ""

    def save(self, key, value):
        """
        Store a value.
        :return:
        """
        self.storage.save("", "", {
            key: value
        })

    def load(self, key, *default):
        """
        Load a value.
        :return:
        """
        try:
            data = self.storage.load("", "")
            return data[key]
        except KeyError as e:
            if len(default) > 0:
                return default[0]
            else:
                raise e
