
"""
Store object's element key data in memory.
"""

from django.conf import settings
from evennia.utils import logger
from muddery.server.utils import utils


class CharacterInventory(object):
    """
    The storage of all objects in characters' inventories.
    """
    def __init__(self, model_name):
        storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
        self.storage = storage_class(model_name, "character_id", "position")

    def get_character(self, character_id):
        """
        Get a character's inventory.
        :param character_id:
        :return:
        """
        return self.storage.load_category_dict(character_id)

    def get_object(self, character_id, position):
        """
        Get an object's info in the inventory.
        :param character_id: (int) character's id
        :param position: (int) position in the inventory
        :return:
        """
        return self.storage.load_dict(character_id, position)

    def add(self, character_id, position, object_key, number, level):
        """
        Add a new object to the inventory.
        :param character_id:
        :param object_key:
        :return:
        """
        self.storage.add_dict(character_id, position, {
            "object_key": object_key,
            "number": number,
            "level": level,
        })

    def set(self, character_id, position, object_key, number, level):
        """
        Set a object's data.

        :param character_id:
        :param object_key:
        :param values:
        :return:
        """
        self.storage.save_dict(character_id, position, {
            "object_key": object_key,
            "number": number,
            "level": level,
        })

    def set_dict(self, character_id, position, values):
        """
        Set a object's data.

        :param character_id:
        :param position:
        :param values:
        :return:
        """
        self.storage.save_dict(character_id, position, values)

    def remove_character(self, character_id):
        """
        Remove a character's all quests.

        :param character_id:
        :return:
        """
        self.storage.delete_category(character_id)

    def remove_object(self, character_id, position):
        """
        Remove a quest

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        self.storage.delete(character_id, position)


CHARACTER_INVENTORY_DATA = CharacterInventory("character_inventory")
