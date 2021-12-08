
"""
Store object's element key data in memory.
"""

from django.conf import settings
from muddery.server.utils import utils


class CharacterEquipments(object):
    """
    The storage of all objects in characters' equipments.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    session = settings.GAME_DATA_APP
    config = settings.AL_DATABASES[session]
    storage = storage_class(session, config["MODELS"], "character_equipments", "character_id", "position")

    @classmethod
    def get_character(cls, character_id):
        """
        Get a character's inventory.
        :param character_id:
        :return:
        """
        return cls.storage.load_category(character_id, {})

    @classmethod
    def get_equipment(cls, character_id, position):
        """
        Get an equipment's info in the inventory.
        :param character_id: (int) character's id
        :param position: (string) position on the body
        :return:
        """
        return cls.storage.load(character_id, position)

    @classmethod
    def add(cls, character_id, position, object_key, level):
        """
        Add a new object to the inventory.
        :param character_id:
        :param object_key:
        :return:
        """
        cls.storage.add(character_id, position, {
            "object_key": object_key,
            "level": level,
        })

    @classmethod
    def set(cls, character_id, position, object_key, level):
        """
        Set a object's data.

        :param character_id:
        :param object_key:
        :param values:
        :return:
        """
        cls.storage.save(character_id, position, {
            "object_key": object_key,
            "level": level,
        })

    @classmethod
    def remove_character(cls, character_id):
        """
        Remove a character's all equipments.

        :param character_id:
        :return:
        """
        cls.storage.delete_category(character_id)

    @classmethod
    def remove_equipment(cls, character_id, position):
        """
        Remove an equipment.

        :param character_id:
        :param position: (string) position on the body
        :return:
        """
        cls.storage.delete(character_id, position)
