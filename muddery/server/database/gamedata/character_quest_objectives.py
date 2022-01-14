
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class CharacterQuestObjectives(BaseData, Singleton):
    """
    The storage of all character's quest's objectives.
    """
    __table_name = "character_quest_objectives"
    __category_name = "character_quest"
    __key_field = "objective"
    __default_value_field = "progress"

    def __init__(self):
        # data storage
        super(CharacterQuestObjectives, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def get_character_quest(self, character_id, quest):
        """
        Get a character's quest objectives.
        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        character_quest = "%s:%s" % (character_id, quest)
        return await self.storage.load_category(character_quest, {})

    async def save_progress(self, character_id, quest, objective_type, object_key, progress):
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
        await self.storage.save(character_quest, objective, progress)

    async def get_progress(self, character_id, quest, objective_type, object_key, *default):
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
        return await self.storage.load(character_quest, objective, *default)

    async def remove(self, character_id, quest):
        """
        Remove a quest's all objectives

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        character_quest = "%s:%s" % (character_id, quest)
        await self.storage.delete_category(character_quest)
