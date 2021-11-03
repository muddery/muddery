
"""
Store object's element key data in memory.
"""

import datetime
from django.conf import settings
from muddery.server.utils import utils


class Accounts(object):
    """
    The storage of player accounts.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT_NO_CACHE)
    storage = storage_class("accounts", "", "username")

    @classmethod
    def add(cls, username, password, account_id, type):
        """
        Add a new account.

        :param username: account's username
        :param password: account's password
        :param account_id: account's id
        :return:
        """
        current_time = datetime.datetime.now()
        cls.storage.add("", username, {
            "password": password,
            "account_id": account_id,
            "type": type,
            "create_time": current_time,
            "last_login": current_time,
        })

    @classmethod
    def remove(cls, username):
        """
        Remove an account.

        :param username: account's username
        """
        cls.storage.delete("", username)

    @classmethod
    def has(cls, username):
        """
        Check if this username exists.

        Args:
            username: (string) username.
        """
        return cls.storage.has("", username)

    @classmethod
    def get_password(cls, username):
        """
        Get an account's password.
        :param username:
        :return:
        """
        data = cls.storage.load("", username)
        return data["password"]

    @classmethod
    def get_info(cls, username):
        """
        Get an account's information.
        :param username:
        :return:
        """
        data = cls.storage.load("", username)
        return {
            "id": data["account_id"],
            "type": data["type"],
        }

    @classmethod
    def update_login_time(cls, username):
        """
        Update the account's last login time.
        """
        current_time = datetime.datetime.now()
        cls.storage.save("", username, {
            "last_login": current_time,
        })
