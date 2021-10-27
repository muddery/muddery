
"""
Store object's element key data in memory.
"""

from django.conf import settings
from muddery.server.utils import utils


class CharacterInfo(object):
    """
    The storage of player character's basic data.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    storage = storage_class("character_info", "", "char_id")

    nicknames = {info["nickname"]: char_id for char_id, info in storage.load_category("", {}).items()}

    @classmethod
    def add(cls, char_id, nickname="", level=1):
        """
        Add a new player character.
        :param char_id:
        :param nickname:
        :return:
        """
        cls.storage.add("", char_id, {
            "nickname": nickname,
            "level": level,
        })
        if nickname:
            cls.nicknames[nickname] = char_id

    @classmethod
    def set_nickname(cls, char_id, nickname):
        """
        Update a character's nickname.
        :param char_id:
        :param nickname:
        :return:
        """
        current_data = cls.storage.load("", char_id, None)
        cls.storage.save("", char_id, {"nickname": nickname})

        if current_data and current_data["nickname"]:
            del cls.nicknames[current_data["nickname"]]
        cls.nicknames[nickname] = char_id

    @classmethod
    def remove_character(cls, char_id):
        """
        Remove an object.
        :param char_id:
        :return:
        """
        current_info = cls.storage.load("", char_id)
        cls.storage.delete("", char_id)

        if current_info["nickname"]:
            del cls.nicknames[current_info["nickname"]]

    @classmethod
    def get_nickname(cls, char_id):
        """
        Get a player character's nickname.
        :param char_id:
        :return:
        """
        data = cls.storage.load("", char_id)
        return data["nickname"]

    @classmethod
    def get_char_id(cls, nickname):
        """
        Get an player character's id by its nickname.
        :param nickname:
        :return:
        """
        return cls.nicknames[nickname]

    @classmethod
    def set_level(cls, char_id, level):
        """
        Set a character's level data.
        :param char_id:
        :param nickname:
        :return:
        """
        cls.storage.save("", char_id, {"level": level})

    @classmethod
    def get_level(cls, char_id):
        """
        Get a player character's level.
        :param char_id:
        :return:
        """
        data = cls.storage.load("", char_id)
        return data["level"]
