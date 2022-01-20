
"""
Store object's element key data in memory.
"""

import datetime
from sqlalchemy import select, update, delete, func
from muddery.server.utils.singleton import Singleton
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.database.db_manager import DBManager
from muddery.worldeditor.database.worldeditor_models import accounts


class Accounts(Singleton):
    """
    The storage of player accounts.
    """
    # data storage
    def __init__(self):
        self.session = DBManager.inst().get_session(SETTINGS.WORLD_EDITOR_APP)

    def add(self, username, password, salt, account_type):
        """
        Add a new account.

        :param username: account's username
        :param password: account's password
        :param account_type: account's type
        :return:
        """
        current_time = datetime.datetime.now()
        data = {
            "username": username,
            "password": password,
            "salt": salt,
            "type": account_type,
            "create_time": current_time,
            "last_login": current_time,
        }

        record = accounts(**data)
        self.session.add(record)

    def remove(self, username):
        """
        Remove an account.

        :param username: account's username
        """
        stmt = delete(accounts).where(accounts.username == username)
        self.session.execute(stmt)

    def count(self):
        """
        Count total data.
        """
        stmt = select(func.count()).select_from(accounts)
        result = self.session.execute(stmt)
        record = result.scalars().one()
        return record > 0

    def has(self, username):
        """
        Check if this username exists.

        Args:
            username: (string) username.
        """
        stmt = select(func.count()).select_from(accounts).where(accounts.username == username)
        result = self.session.execute(stmt)
        record = result.scalars().one()
        return record > 0

    def get_password(self, username):
        """
        Get an account's password.
        :param username:
        :return:
        """
        stmt = select(accounts).where(accounts.username == username)
        result = self.session.execute(stmt)
        record = result.scalars().one()
        return record.password, record.salt

    def set_password(self, username, password):
        """
        Set a new password.
        :param username:
        :return:
        """
        stmt = update(accounts).where(accounts.username == username).values(
            username=username,
            password=password,
        )

        self.session.execute(stmt)

    def get_type(self, username):
        """
        Get an account's information.
        :param username:
        :return:
        """
        stmt = select(accounts).where(accounts.username == username)
        result = self.session.execute(stmt)
        record = result.scalars().one()
        return record.type

    def update_login(self, username, token):
        """
        Update the account's last login time.
        """
        current_time = datetime.datetime.now()
        stmt = update(accounts).where(accounts.username == username).values(
            last_login=current_time,
            token=token
        )

        self.session.execute(stmt)

    def get_last_token(self, username):
        """
        Get an account's information.
        :param username:
        :return:
        """
        stmt = select(accounts).where(accounts.username == username)
        result = self.session.execute(stmt)
        record = result.scalars().one()
        return record.token

    def set_last_token(self, username, token):
        """
        Set the token of the last login.
        :param username:
        :param token:
        :return:
        """
        stmt = update(accounts).where(accounts.username == username).values(
            token=token
        )

        self.session.execute(stmt)
