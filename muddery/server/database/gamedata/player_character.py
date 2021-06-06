
"""
Store object's element key data in memory.
"""

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger
from muddery.server.utils import utils


class PlayerCharacter(object):
    """
    The storage of player character's basic data.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    storage = storage_class("player_character", "account_id", "char_id")

    nicknames = {item["nickname"]: key for account, data in storage.all().items() for key, item in data.items()}

    @classmethod
    def add(cls, account_id, char_id, nickname="", level=1):
        """
        Add a new player character.
        :param char_id:
        :param nickname:
        :return:
        """
        cls.storage.add(account_id, char_id, {
            "nickname": nickname,
            "level": level,
        })
        if nickname:
            cls.nicknames[nickname] = char_id

    @classmethod
    def set_nickname(cls, account_id, char_id, nickname):
        """
        Update a character's nickname.
        :param char_id:
        :param nickname:
        :return:
        """
        current_data = cls.storage.load(account_id, char_id, None)
        cls.storage.save(account_id, char_id, {"nickname": nickname})

        if current_data and current_data["nickname"]:
            del cls.nicknames[current_data["nickname"]]
        cls.nicknames[nickname] = char_id

    @classmethod
    def remove_character(cls, account_id, char_id):
        """
        Remove an object.
        :param char_id:
        :return:
        """
        current_info = cls.storage.load(account_id, char_id)
        cls.storage.delete(account_id, char_id)

        if current_info["nickname"]:
            del cls.nicknames[current_info["nickname"]]

    @classmethod
    def get_account_characters(cls, account_id):
        """
        Get all characters of an account.
        :param account_id:
        :return:
        """
        data = cls.storage.load_category(account_id, {})
        return data

    @classmethod
    def get_nickname(cls, account_id, char_id):
        """
        Get a player character's nickname.
        :param char_id:
        :return:
        """
        data = cls.storage.load(account_id, char_id)
        return data["nickname"]

    @classmethod
    def get_char_id(cls, nickname):
        """
        Get an player character's id by its nickname.
        :param key:
        :return:
        """
        return cls.nicknames[nickname]

    @classmethod
    def set_level(cls, account_id, char_id, level):
        """
        Set a character's level data.
        :param char_id:
        :param nickname:
        :return:
        """
        cls.storage.save(account_id, char_id, {"level": level})

    @classmethod
    def get_level(cls, account_id, char_id):
        """
        Get a player character's level.
        :param char_id:
        :return:
        """
        data = cls.storage.load(account_id, char_id)
        return data["level"]
