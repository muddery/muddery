
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class CharacterEquipments(BaseData, Singleton):
    """
    The storage of all objects in characters' equipments.
    """
    __table_name = "character_equipments"
    __category_name = "character_id"
    __key_field = "position"
    __default_value_field = ""

    def get_character(self, character_id):
        """
        Get a character's inventory.
        :param character_id:
        :return:
        """
        return self.storage.load_category(character_id, {})

    def get_equipment(self, character_id, position):
        """
        Get an equipment's info in the inventory.
        :param character_id: (int) character's id
        :param position: (string) position on the body
        :return:
        """
        return self.storage.load(character_id, position)

    def add(self, character_id, position, object_key, level):
        """
        Add a new object to the inventory.
        :param character_id:
        :param object_key:
        :return:
        """
        self.storage.add(character_id, position, {
            "object_key": object_key,
            "level": level,
        })

    def set(self, character_id, position, object_key, level):
        """
        Set a object's data.

        :param character_id:
        :param object_key:
        :param values:
        :return:
        """
        self.storage.save(character_id, position, {
            "object_key": object_key,
            "level": level,
        })

    def remove_character(self, character_id):
        """
        Remove a character's all equipments.

        :param character_id:
        :return:
        """
        self.storage.delete_category(character_id)

    def remove_equipment(self, character_id, position):
        """
        Remove an equipment.

        :param character_id:
        :param position: (string) position on the body
        :return:
        """
        self.storage.delete(character_id, position)
