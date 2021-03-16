
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
    def __init__(self, model_name):
        storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
        self.storage = storage_class(model_name, "", "object_id")

        all_data = self.storage.load_category_dict("")
        self.nicknames = {item["nickname"]: key for key, item in all_data.items()}

    def add(self, object_id, nickname=""):
        """
        Store an object's key.
        :param object_id:
        :param nickname:
        :return:
        """
        self.storage.add_dict("", object_id, {"nickname": nickname})
        if nickname:
            self.nicknames[nickname] = object_id

    def update_nickname(self, object_id, nickname):
        """
        Update a character's nickname.
        :param object_id:
        :param nickname:
        :return:
        """
        current_info = self.storage.load_dict("", object_id)
        self.storage.save_dict("", object_id, {"nickname": nickname})

        if current_info["nickname"]:
            del self.nicknames[current_info["nickname"]]
        self.nicknames[nickname] = object_id

    def remove(self, object_id):
        """
        Remove an object.
        :param object_id:
        :return:
        """
        current_info = self.storage.load_dict("", object_id)
        self.storage.delete("", object_id)

        if current_info["nickname"]:
            del self.nicknames[current_info["nickname"]]

    def get_nickname(self, object_id):
        """
        Get a player character's nickname.
        :param object_id:
        :return:
        """
        info = self.storage.load_dict("", object_id)
        return info["nickname"]

    def get_object_id(self, nickname):
        """
        Get an player character's id by its nickname.
        :param key:
        :return:
        """
        return self.nicknames[nickname]


PLAYER_CHARACTER_DATA = PlayerCharacter("player_character")
