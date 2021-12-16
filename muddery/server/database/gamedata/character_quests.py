
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class CharacterQuests(BaseData, Singleton):
    """
    The storage of all character's quest's objectives.
    """
    __table_name = "character_quests"
    __category_name = "character_id"
    __key_field = "quest"
    __default_value_field = ""

    def get_character(self, character_id):
        """
        Get a character's quest info.
        :param character_id:
        :return:
        """
        return self.storage.load_category(character_id, {})

    def get_quest(self, character_id, quest):
        """
        Get a character's quest info.
        :param character_id: (int) character's id
        :param quest: (string) quest's key
        :return:
        """
        return self.storage.load(character_id, quest)

    def add(self, character_id, quest):
        """
        Add a new quest.
        :param character_id:
        :param quest:
        :return:
        """
        self.storage.add(character_id, quest, {"finished": False})

    def set(self, character_id, quest, values):
        """
        Set a quest's data.

        :param character_id:
        :param quest:
        :param values:
        :return:
        """
        self.storage.save(character_id, quest, values)

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
