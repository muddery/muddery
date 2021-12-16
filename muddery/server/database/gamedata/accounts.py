
"""
Store object's element key data in memory.
"""

import datetime
from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class Accounts(BaseData, Singleton):
    """
    The storage of player accounts.
    """
    __table_name = "accounts"
    __category_name = ""
    __key_field = "username"
    __default_value_field = ""

    def add(self, username, password, account_id, type):
        """
        Add a new account.

        :param username: account's username
        :param password: account's password
        :param account_id: account's id
        :return:
        """
        current_time = datetime.datetime.now()
        self.storage.add("", username, {
            "password": password,
            "account_id": account_id,
            "type": type,
            "create_time": current_time,
            "last_login": current_time,
        })

    def remove(self, username):
        """
        Remove an account.

        :param username: account's username
        """
        self.storage.delete("", username)

    def has(self, username):
        """
        Check if this username exists.

        Args:
            username: (string) username.
        """
        return self.storage.has("", username)

    def get_password(self, username):
        """
        Get an account's password.
        :param username:
        :return:
        """
        data = self.storage.load("", username)
        return data["password"]

    def set_password(self, username, password):
        """
        Set a new password.
        :param username:
        :return:
        """
        self.storage.save("", username, {
            "password": password,
        })

    def get_info(self, username):
        """
        Get an account's information.
        :param username:
        :return:
        """
        data = self.storage.load("", username)
        return {
            "id": data["account_id"],
            "type": data["type"],
        }

    def update_login_time(self, username):
        """
        Update the account's last login time.
        """
        current_time = datetime.datetime.now()
        self.storage.save("", username, {
            "last_login": current_time,
        })
