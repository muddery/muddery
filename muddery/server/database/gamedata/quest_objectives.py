
"""
Store object's element key data in memory.
"""

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger


class QuestObjectives(object):
    """
    The storage of all character's quest's objectives.
    """
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = apps.get_model(settings.GAME_DATA_APP, model_name)
        self.characters = {}

        # load data
        for record in self.model.objects.all():
            if record.character_id not in self.characters:
                self.characters[record.character_id] = {}
            if record.quest not in self.characters[record.character_id]:
                self.characters[record.character_id][record.quest] = {}

            self.characters[record.character_id][record.quest][(record.objective_type, record.object_key)] = record.progress

    def get_character(self, character_id):
        """
        Get a character's quest objectives.
        :param character_id:
        :return:
        """
        return self.characters.get(character_id, {}).copy()

    def get_character_quest(self, character_id, quest):
        """
        Get a character's quest objectives.
        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        try:
            return self.characters[character_id][quest].copy()
        except KeyError:
            return {}

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
        try:
            records = self.model.objects.filter(character_id=character_id, quest=quest, objective_type=objective_type,
                                                object_key=object_key)
            if records:
                records.update(progress=progress)
            else:
                record = self.model(
                    character_id=character_id,
                    quest=quest,
                    objective_type=objective_type,
                    object_key=object_key,
                    progress=progress
                )
                record.save()

            if character_id not in self.characters:
                self.characters[character_id] = {}
            if quest not in self.characters[character_id]:
                self.characters[character_id][quest] = {}
            self.characters[character_id][quest][(objective_type, object_key)] = progress
        except Exception:
            logger.log_err("Can not save objective: %s %s %s %s %s" % (character_id, quest, objective_type, object_key,
                                                                       progress))

    def remove(self, character_id, quest):
        """
        Remove a quest's all objectives

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        self.model.objects.filter(character_id=character_id, quest=quest).delete()


QUEST_OBJECTIVES_DATA = QuestObjectives("quest_objectives")
