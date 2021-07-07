
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
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    storage = storage_class("character_inventory", "character_id", "position")

    @classmethod
    def get_character(cls, character_id):
        """
        Get a character's inventory.
        :param character_id:
        :return:
        """
        return cls.storage.load_category(character_id, {})

    @classmethod
    def get_object(cls, character_id, position):
        """
        Get an object's info in the inventory.
        :param character_id: (int) character's id
        :param position: (int) position in the inventory
        :return:
        """
        return cls.storage.load(character_id, position)

    @classmethod
    def add(cls, character_id, position, object_key, number, level):
        """
        Add a new object to the inventory.
        :param character_id:
        :param object_key:
        :return:
        """
        cls.storage.add(character_id, position, {
            "object_key": object_key,
            "number": number,
            "level": level,
        })

    @classmethod
    def set(cls, character_id, position, object_key, number, level):
        """
        Set a object's data.

        :param character_id:
        :param object_key:
        :param values:
        :return:
        """
        cls.storage.save(character_id, position, {
            "object_key": object_key,
            "number": number,
            "level": level,
        })

    @classmethod
    def set_dict(cls, character_id, position, values):
        """
        Set a object's data.

        :param character_id:
        :param position:
        :param values:
        :return:
        """
        cls.storage.save(character_id, position, values)

    @classmethod
    def remove_character(cls, character_id):
        """
        Remove a character's all objects.

        :param character_id: character's db id
        :return:
        """
        cls.storage.delete_category(character_id)

    @classmethod
    def remove_object(cls, character_id, position):
        """
        Remove an object.

        :param character_id:
        :param position: (int) object's position in the inventory
        :return:
        """
        cls.storage.delete(character_id, position)
