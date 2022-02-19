
"""
Store object's element key data in memory.
"""

import datetime
from muddery.server.database.gamedata.base_data import BaseData
from muddery.common.utils.singleton import Singleton


class Accounts(BaseData, Singleton):
    """
    The storage of player accounts.
    """
    __table_name = "accounts"
    __category_name = None
    __key_field = "username"
    __default_value_field = None

    def __init__(self):
        # data storage
        super(Accounts, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def add(self, username, password, salt, account_id, type):
        """
        Add a new account.

        :param username: account's username
        :param password: account's password
        :param account_id: account's id
        :return:
        """
        current_time = datetime.datetime.now()
        await self.storage.add("", username, {
            "password": password,
            "salt": salt,
            "account_id": account_id,
            "type": type,
            "create_time": current_time,
        })

    async def remove(self, username):
        """
        Remove an account.

        :param username: account's username
        """
        await self.storage.delete("", username)

    async def has(self, username):
        """
        Check if this username exists.

        Args:
            username: (string) username.
        """
        return await self.storage.has("", username)

    async def get_password(self, username):
        """
        Get an account's password.
        :param username:
        :return:
        """
        data = await self.storage.load("", username)
        return data["password"], data["salt"]

    async def set_password(self, username, password, salt):
        """
        Set a new password.
        :param username:
        :return:
        """
        await self.storage.save("", username, {
            "password": password,
            "salt": salt,
        })

    async def get_info(self, username):
        """
        Get an account's information.
        :param username:
        :return:
        """
        data = await self.storage.load("", username)
        return {
            "id": data["account_id"],
            "type": data["type"],
        }

    async def update_login_time(self, username):
        """
        Update the account's last login time.
        """
        current_time = datetime.datetime.now()
        await self.storage.save("", username, {
            "last_login": current_time,
        })
