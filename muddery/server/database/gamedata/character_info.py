
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.common.utils.singleton import Singleton


class CharacterInfo(BaseData, Singleton):
    """
    The storage of player character's basic data.
    """
    __table_name = "character_info"
    __category_name = None
    __key_field = "character_id"
    __default_value_field = None

    def __init__(self):
        super(CharacterInfo, self).__init__()

        self.nicknames = {}
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def init(self):
        char_info = await self.storage.load_category("", {})
        self.nicknames = {info["nickname"]: char_id for char_id, info in char_info.items()}

    async def add(self, char_id, element_type, element_key, nickname="", level=1):
        """
        Add a new player character.
        :param char_id:
        :param nickname:
        :return:
        """
        await self.storage.add("", char_id, {
            "element_type": element_type,
            "element_key": element_key,
            "nickname": nickname,
            "level": level,
        })
        if nickname:
            self.nicknames[nickname] = char_id

    async def set_nickname(self, char_id, nickname):
        """
        Update a character's nickname.
        :param char_id:
        :param nickname:
        :return:
        """
        current_data = await self.storage.load("", char_id, None)
        await self.storage.save("", char_id, {"nickname": nickname})

        if current_data and current_data["nickname"]:
            del self.nicknames[current_data["nickname"]]
        self.nicknames[nickname] = char_id

    async def remove_character(self, char_id):
        """
        Remove an object.
        :param char_id:
        :return:
        """
        current_info = await self.storage.load("", char_id)
        await self.storage.delete("", char_id)

        if current_info["nickname"]:
            del self.nicknames[current_info["nickname"]]

    async def get(self, char_id):
        """
        Get a player character's nickname.
        :param char_id:
        :return:
        """
        return await self.storage.load("", char_id)

    async def get_nickname(self, char_id):
        """
        Get a player character's nickname.
        :param char_id:
        :return:
        """
        data = await self.storage.load("", char_id)
        return data["nickname"]

    async def get_char_id(self, nickname):
        """
        Get an player character's id by its nickname.
        :param nickname:
        :return:
        """
        return self.nicknames[nickname]

    async def set_level(self, char_id, level):
        """
        Set a character's level data.
        :param char_id:
        :param nickname:
        :return:
        """
        await self.storage.save("", char_id, {"level": level})

    async def get_level(self, char_id):
        """
        Get a player character's level.
        :param char_id:
        :return:
        """
        data = await self.storage.load("", char_id)
        return data["level"]
