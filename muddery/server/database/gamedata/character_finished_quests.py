
"""
The storage of all character's quests that are finished.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.common.utils.singleton import Singleton


class CharacterFinishedQuests(BaseData, Singleton):
    """
    The storage of all character's quests that are finished.
    """
    __table_name = "character_finished_quests"
    __category_name = "character_id"
    __key_field = "quest"
    __default_value_field = None

    def __init__(self):
        # data storage
        super(CharacterFinishedQuests, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def get_character(self, character_id):
        """
        Get a character's quest info.
        :param character_id:
        :return:
        """
        return await self.storage.load_category(character_id, {})

    async def has(self, character_id, quest):
        """
        Check if the character has this quest.
        :param character_id:
        :param quest:
        :return:
        """
        return await self.storage.has(character_id, quest)

    async def add(self, character_id, quest):
        """
        Add a new quest.
        :param character_id:
        :param quest:
        :return:
        """
        await self.storage.add(character_id, quest)

    async def remove_character(self, character_id):
        """
        Remove a character's all quests.

        :param character_id:
        :return:
        """
        await self.storage.delete_category(character_id)

    async def remove(self, character_id, quest):
        """
        Remove a quest

        :param character_id:
        :param quest: (string) quest's key
        :return:
        """
        await self.storage.delete(character_id, quest)
