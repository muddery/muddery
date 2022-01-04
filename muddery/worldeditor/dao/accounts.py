
"""
Store object's element key data in memory.
"""

import datetime
from sqlalchemy import select, update, delete, func
from django.conf import settings
from muddery.server.utils.singleton import Singleton
from muddery.worldeditor.database.db_manager import DBManager
from muddery.worldeditor.database.worldeditor_models import accounts


class Accounts(Singleton):
    """
    The storage of player accounts.
    """
    # data storage
    def __init__(self):
        self.session = DBManager.inst().get_session(settings.WORLD_EDITOR_APP)

    def add(self, username, password, type):
        """
        Add a new account.

        :param username: account's username
        :param password: account's password
        :param account_id: account's id
        :return:
        """
        current_time = datetime.datetime.now()
        data = {
            "username": username,
            "password": password,
            "type": type,
            "create_time": current_time,
            "last_login": current_time,
        }

        record = accounts(**data)

        try:
            self.session.add(record)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

    def remove(self, username):
        """
        Remove an account.

        :param username: account's username
        """
        stmt = delete(accounts).where(accounts.username == username)

        try:
            result = self.session.execute(stmt)
            if result.rowcount > 0:
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

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
        return result.scalars().one().password

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

        try:
            result = self.session.execute(stmt)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

    def get_info(self, username):
        """
        Get an account's information.
        :param username:
        :return:
        """
        stmt = select(accounts).where(accounts.username == username)
        result = self.session.execute(stmt)
        record = result.scalars().one()
        return {
            "type": record.type,
        }

    def update_login_time(self, username):
        """
        Update the account's last login time.
        """
        current_time = datetime.datetime.now()
        stmt = update(accounts).where(accounts.username == username).values(
            last_login=current_time,
        )

        try:
            result = self.session.execute(stmt)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise
