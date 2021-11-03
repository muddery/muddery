
"""
Store object's element key data in memory.
"""

from django.conf import settings
from muddery.server.utils import utils


class AccountCharacters(object):
    """
    The storage of account's characters.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    storage = storage_class("account_characters", "account_id", "")

    @classmethod
    def add(cls, account_id, char_id):
        """
        Add a new player character.

        :param account_id: player's account id
        :param char_id: character's db id
        :return:
        """
        cls.storage.add(account_id, char_id)

    @classmethod
    def remove_character(cls, account_id, char_id):
        """
        Remove an character.

        :param account_id: player's account id
        :param char_id: character's db id
        :return:
        """
        cls.storage.delete(account_id, char_id)

    @classmethod
    def get_account_characters(cls, account_id):
        """
        Get all characters of an account.
        :param account_id:
        :return:
        """
        return cls.storage.load_category(account_id, {})
