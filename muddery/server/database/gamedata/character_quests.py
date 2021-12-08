
"""
Store object's element key data in memory.
"""

from django.conf import settings
from muddery.server.utils import utils


class CharacterQuests(object):
    """
    The storage of all character's quest's objectives.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    session = settings.GAME_DATA_APP
    config = settings.AL_DATABASES[session]
    storage = storage_class(session, config["MODELS"], "character_quests", "character_id", "quest")

    @classmethod
    def get_character(cls, character_id):
        """
        Get a character's quest info.
        :param character_id:
        :return:
        """
        return cls.storage.load_category(character_id, {})

    @classmethod
    def get_quest(cls, character_id, quest):
        """
        Get a character's quest info.
        :param character_id: (int) character's id
        :param quest: (string) quest's key
        :return:
        """
        return cls.storage.load(character_id, quest)

    @classmethod
    def add(cls, character_id, quest):
        """
        Add a new quest.
        :param character_id:
        :param quest:
        :return:
        """
        cls.storage.add(character_id, quest, {"finished": False})

    @classmethod
    def set(cls, character_id, quest, values):
        """
        Set a quest's data.

        :param character_id:
        :param quest:
        :param values:
        :return:
        """
        cls.storage.save(character_id, quest, values)

    @classmethod
    def remove_character(cls, character_id):
        """
        Remove a character's all quests.

        :param character_id:
        :return:
        """
        cls.storage.delete_category(character_id)

    @classmethod
    def remove_quest(cls, character_id, quest):
        """
        Remove a quest

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        cls.storage.delete(character_id, quest)
