
"""
Store object's element key data in memory.
"""

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger
from muddery.server.utils import utils


class QuestObjectives(object):
    """
    The storage of all character's quest's objectives.
    """
    def __init__(self, model_name):
        storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
        self.storage = storage_class(model_name, "character_quest", "objective", "progress")

    def get_character_quest(self, character_id, quest):
        """
        Get a character's quest objectives.
        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        character_quest = "%s:%s" % (character_id, quest)
        return self.storage.load_category(character_quest)

    def save_progress(self, character_id, quest, objective_type, object_key, progress):
        """
        Save new progress.
        :param character_id:
        :param quest:
        :param objective_type:
        :param object_key:
        :param progress:
        :return:
        """
        character_quest = "%s:%s" % (character_id, quest)
        objective = "%s:%s" % (objective_type, object_key)
        self.storage.save(character_quest, objective, progress)

    def get_progress(self, character_id, quest, objective_type, object_key, *default):
        """
        Save new progress.
        :param character_id:
        :param quest:
        :param objective_type:
        :param object_key:
        :param progress:
        :return:
        """
        character_quest = "%s:%s" % (character_id, quest)
        objective = "%s:%s" % (objective_type, object_key)
        return self.storage.load(character_quest, objective, *default)

    def remove(self, character_id, quest):
        """
        Remove a quest's all objectives

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        character_quest = "%s:%s" % (character_id, quest)
        self.storage.delete_category(character_quest)


QUEST_OBJECTIVES_DATA = QuestObjectives("quest_objectives")
