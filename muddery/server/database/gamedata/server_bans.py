
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class ServerBans(BaseData, Singleton):
    """
    The storage of player accounts.
    """
    __table_name = "server_bans"
    __category_name = "type"
    __key_field = "target"
    __default_value_field = None

    def __init__(self):
        # data storage
        super(ServerBans, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    def add(self, ban_type, ban_target, finish_time):
        """
        Add a new ban.

        :return:
        """
        self.storage.add(ban_type, ban_target, {
            "finish_time": finish_time,
        })

    def remove(self, ban_type, ban_target):
        """
        Remove a ban.

        :param username: account's username
        """
        self.storage.delete(ban_type, ban_target)

    async def get_ban_time(self, ban_type, ban_target):
        """
        Get a ban's finish time.
        :param username:
        :return:
        """
        data = await self.storage.load(ban_type, ban_target)
        return data["finish_time"]
