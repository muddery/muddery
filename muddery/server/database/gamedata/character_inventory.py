
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class CharacterInventory(BaseData, Singleton):
    """
    The storage of all objects in characters' inventories.
    """
    __table_name = "character_inventory"
    __category_name = "character_id"
    __key_field = "position"
    __default_value_field = None

    def __init__(self):
        # data storage
        super(CharacterInventory, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def get_character(self, character_id):
        """
        Get a character's inventory.
        :param character_id:
        :return:
        """
        return await self.storage.load_category(character_id, {})

    async def get_object(self, character_id, position):
        """
        Get an object's info in the inventory.
        :param character_id: (int) character's id
        :param position: (int) position in the inventory
        :return:
        """
        return await self.storage.load(character_id, position)

    async def add(self, character_id, position, object_key, number, level):
        """
        Add a new object to the inventory.
        :param character_id:
        :param object_key:
        :return:
        """
        await self.storage.add(character_id, position, {
            "object_key": object_key,
            "number": number,
            "level": level,
        })

    async def set(self, character_id, position, object_key, number, level):
        """
        Set a object's data.

        :param character_id:
        :param object_key:
        :param values:
        :return:
        """
        await self.storage.save(character_id, position, {
            "object_key": object_key,
            "number": number,
            "level": level,
        })

    async def set_dict(self, character_id, position, values):
        """
        Set a object's data.

        :param character_id:
        :param position:
        :param values:
        :return:
        """
        await self.storage.save(character_id, position, values)

    async def remove_character(self, character_id):
        """
        Remove a character's all objects.

        :param character_id: character's db id
        :return:
        """
        await self.storage.delete_category(character_id)

    async def remove_object(self, character_id, position):
        """
        Remove an object.

        :param character_id:
        :param position: (int) object's position in the inventory
        :return:
        """
        await self.storage.delete(character_id, position)
