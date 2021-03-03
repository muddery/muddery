
"""
Store object's element key data in memory.
"""

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger


class CharacterQuests(object):
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

            self.characters[record.character_id][record.quest] = {
                "finished": record.finished,
            }

    def get_character(self, character_id):
        """
        Get a character's quest objectives.
        :param character_id:
        :return:
        """
        return self.characters.get(character_id, {}).copy()

    def get_quest(self, character_id, quest):
        """
        Get a character's quest objectives.
        :param character_id:
        :return:
        """
        if character_id not in self.characters or quest not in self.characters[character_id]:
            return
        return self.characters[character_id][quest].copy()

    def add(self, character_id, quest):
        """
        Add a new quest.
        :param character_id:
        :param quest:
        :return:
        """
        records = self.model.objects.filter(character_id=character_id, quest=quest)
        if records:
            raise Exception("Quest already exists.")

        try:
            record = self.model(
                character_id=character_id,
                quest=quest,
                finished=False
            )
            record.save()
        except Exception as e:
            logger.log_err("Can not save quest: %s %s" % (character_id, quest))
            raise e

        if character_id not in self.characters:
            self.characters[character_id] = {}

        self.characters[character_id][quest] = {
            "finished": False
        }

    def set(self, character_id, quest, values):
        """
        Set a quest's data.

        :param character_id:
        :param quest:
        :param values:
        :return:
        """
        records = self.model.objects.filter(character_id=character_id, quest=quest)
        if not records:
            raise Exception("Can not find the quest.")

        try:
            records.update(**values)
        except Exception as e:
            logger.log_err("Can not update quest: %s %s" % (character_id, quest))
            raise e

        if character_id not in self.characters:
            self.characters[character_id] = {}

        self.characters[character_id][quest] = values

    def remove_character(self, character_id):
        """
        Remove a character's all quests.

        :param character_id:
        :return:
        """
        self.model.objects.filter(character_id=character_id).delete()

    def remove_quest(self, character_id, quest):
        """
        Remove a quest

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        self.model.objects.filter(character_id=character_id, quest=quest).delete()


CHARACTER_QUESTS_DATA = CharacterQuests("character_quests")
