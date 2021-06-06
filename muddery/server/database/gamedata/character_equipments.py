
"""
Store object's element key data in memory.
"""

from django.conf import settings
from evennia.utils import logger
from muddery.server.utils import utils


class CharacterEquipments(object):
    """
    The storage of all objects in characters' equipments.
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


CHARACTER_EQUIPMENTS_DATA = CharacterEquipments("character_equipments")
