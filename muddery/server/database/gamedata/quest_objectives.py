
"""
Store object's element key data in memory.
"""

from django.conf import settings
from muddery.server.utils import utils


class QuestObjectives(object):
    """
    The storage of all character's quest's objectives.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    session = settings.GAME_DATA_APP
    config = settings.AL_DATABASES[session]
    storage = storage_class(session, config["MODELS"], "quest_objectives", "character_quest", "objective", "progress")

    @classmethod
    def get_character_quest(cls, character_id, quest):
        """
        Get a character's quest objectives.
        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        character_quest = "%s:%s" % (character_id, quest)
        return cls.storage.load_category(character_quest, {})

    @classmethod
    def save_progress(cls, character_id, quest, objective_type, object_key, progress):
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
        cls.storage.save(character_quest, objective, progress)

    @classmethod
    def get_progress(cls, character_id, quest, objective_type, object_key, *default):
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
        return cls.storage.load(character_quest, objective, *default)

    @classmethod
    def remove(cls, character_id, quest):
        """
        Remove a quest's all objectives

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        character_quest = "%s:%s" % (character_id, quest)
        cls.storage.delete_category(character_quest)
