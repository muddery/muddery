
"""
Store object's element key data in memory.
"""

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger
from muddery.server.utils import utils


class CharacterQuests(object):
    """
    The storage of all character's quest's objectives.
    """
    def __init__(self, model_name):
        storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
        self.storage = storage_class(model_name, "character_id", "quest")

    def get_character(self, character_id):
        """
        Get a character's quest info.
        :param character_id:
        :return:
        """
        return self.storage.load_category_dict(character_id)

    def get_quest(self, character_id, quest):
        """
        Get a character's quest info.
        :param character_id: (int) character's id
        :param quest: (string) quest's key
        :return:
        """
        return self.storage.load_dict(character_id, quest)

    def add(self, character_id, quest):
        """
        Add a new quest.
        :param character_id:
        :param quest:
        :return:
        """
        self.storage.add_dict(character_id, quest, {"finished": False})

    def set(self, character_id, quest, values):
        """
        Set a quest's data.

        :param character_id:
        :param quest:
        :param values:
        :return:
        """
        self.storage.save_dict(character_id, quest, values)

    def remove_character(self, character_id):
        """
        Remove a character's all quests.

        :param character_id:
        :return:
        """
        self.storage.delete_category(character_id)

    def remove_quest(self, character_id, quest):
        """
        Remove a quest

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        self.storage.delete(character_id, quest)


CHARACTER_QUESTS_DATA = CharacterQuests("character_quests")
