
"""
Store object's element key data in memory.
"""

from django.conf import settings
from muddery.server.utils import utils


class ServerBans(object):
    """
    The storage of player accounts.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    session = settings.GAME_DATA_APP
    config = settings.AL_DATABASES[session]
    storage = storage_class(session, config["MODELS"], "server_bans", "type", "target")

    @classmethod
    def add(cls, ban_type, ban_target, finish_time):
        """
        Add a new ban.

        :return:
        """
        cls.storage.add(ban_type, ban_target, {
            "finish_time": finish_time,
        })

    @classmethod
    def remove(cls, ban_type, ban_target):
        """
        Remove a ban.

        :param username: account's username
        """
        cls.storage.delete(ban_type, ban_target)

    @classmethod
    def get_ban_time(cls, ban_type, ban_target):
        """
        Get a ban's finish time.
        :param username:
        :return:
        """
        data = cls.storage.load(ban_type, ban_target)
        return data["finish_time"]
