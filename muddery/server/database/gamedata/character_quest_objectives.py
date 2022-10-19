
"""
Store object's element key data in memory.
"""

import json
from muddery.server.database.gamedata.base_data import BaseData
from muddery.common.utils.singleton import Singleton


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
        data = await self.storage.load(character_id, quest, "{}")
        return json.loads(data)

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
        objective = "%s:%s" % (objective_type, object_key)

        with self.storage.transaction():
            data = await self.storage.load(character_id, quest, "{}", for_update=True)
            objectives = json.loads(data)
            objectives[objective] = progress
            await self.storage.save(character_id, quest, json.dumps(objectives))

    async def get_progress(self, character_id, quest, objective_type, object_key, *default):
        """
        Save new progress.
        :param character_id:
        :param quest:
        :param objective_type:
        :param object_key:
        :return: progress
        """
        objective = "%s:%s" % (objective_type, object_key)
        data = await self.storage.load(character_id, quest, "{}")
        objectives = json.loads(data)
        try:
            return objectives[objective]
        except KeyError:
            if len(default) > 0:
                return default[0]
            raise

    async def remove(self, character_id, quest):
        """
        Remove a quest's all objectives

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        await self.storage.delete(character_id, quest)

    async def remove_character(self, character_id):
        """
        Remove a quest's all objectives

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        await self.storage.delete_category(character_id)
