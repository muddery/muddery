"""
Characters revealed map.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.common.utils.singleton import Singleton


class CharacterRevealedMap(BaseData, Singleton):
    """
    Player character's location.
    """
    __table_name = "character_revealed_map"
    __category_name = "character_id"
    __key_field = "map_key"
    __default_value_field = "map_key"

    def __init__(self):
        # data storage
        super(CharacterRevealedMap, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def get_character(self, character_id):
        """
        Get a character's revealed map.
        :param character_id:
        :return:
        """
        return await self.storage.load_category(character_id, {})

    async def has(self, character_id, map_key):
        """
        Get a character's map info.
        :param character_id: (int) character's id
        :param map_key: (string) map's key
        :return:
        """
        return await self.storage.has(character_id, map_key)

    async def add(self, character_id, map_key):
        """
        Add a new revealed map.
        :param character_id:
        :param map_key:
        :return:
        """
        await self.storage.add(character_id, map_key)

    async def remove_character(self, character_id):
        """
        Remove a character's all maps.

        :param character_id:
        :return:
        """
        await self.storage.delete_category(character_id)

    async def remove(self, character_id, map_key):
        """
        Remove a map.

        :param character_id:
        :param map_key: (string) map's key
        :return:
        """
        await self.storage.delete(character_id, map_key)
