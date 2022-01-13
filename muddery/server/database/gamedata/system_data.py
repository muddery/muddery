
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
    __category_name = None
    __key_field = None
    __default_value_field = None

    def __init__(self):
        # data storage
        super(SystemData, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def save(self, key, value):
        """
        Store a value.
        :return:
        """
        await self.storage.save("", "", {key: value})

    async def load(self, key, *default, for_update=False):
        """
        Load a value.
        :return:
        """
        try:
            data = await self.storage.load("", "", {}, for_update=for_update)
            return data[key]
        except KeyError as e:
            if len(default) > 0:
                return default[0]
            else:
                raise e
