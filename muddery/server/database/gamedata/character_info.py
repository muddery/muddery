
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class CharacterInfo(BaseData, Singleton):
    """
    The storage of player character's basic data.
    """
    __table_name = "character_info"
    __category_name = ""
    __key_field = "char_id"
    __default_value_field = ""

    def __init__(self):
        super(CharacterInfo, self).__init__()

        self.nicknames = {info["nickname"]: char_id for char_id, info in self.storage.load_category("", {}).items()}

    def add(self, char_id, nickname="", level=1):
        """
        Add a new player character.
        :param char_id:
        :param nickname:
        :return:
        """
        self.storage.add("", char_id, {
            "nickname": nickname,
            "level": level,
        })
        if nickname:
            self.nicknames[nickname] = char_id

    def set_nickname(self, char_id, nickname):
        """
        Update a character's nickname.
        :param char_id:
        :param nickname:
        :return:
        """
        current_data = self.storage.load("", char_id, None)
        self.storage.save("", char_id, {"nickname": nickname})

        if current_data and current_data["nickname"]:
            del self.nicknames[current_data["nickname"]]
        self.nicknames[nickname] = char_id

    def remove_character(self, char_id):
        """
        Remove an object.
        :param char_id:
        :return:
        """
        current_info = self.storage.load("", char_id)
        self.storage.delete("", char_id)

        if current_info["nickname"]:
            del self.nicknames[current_info["nickname"]]

    def get_nickname(self, char_id):
        """
        Get a player character's nickname.
        :param char_id:
        :return:
        """
        data = self.storage.load("", char_id)
        return data["nickname"]

    def get_char_id(self, nickname):
        """
        Get an player character's id by its nickname.
        :param nickname:
        :return:
        """
        return self.nicknames[nickname]

    def set_level(self, char_id, level):
        """
        Set a character's level data.
        :param char_id:
        :param nickname:
        :return:
        """
        self.storage.save("", char_id, {"level": level})

    def get_level(self, char_id):
        """
        Get a player character's level.
        :param char_id:
        :return:
        """
        data = self.storage.load("", char_id)
        return data["level"]
