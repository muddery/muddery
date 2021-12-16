
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class AccountCharacters(BaseData, Singleton):
    """
    The storage of account's characters.
    """
    __table_name = "account_characters"
    __category_name = "account_id"
    __key_field = "char_id"
    __default_value_field = ""

    def add(self, account_id, char_id):
        """
        Add a new player character.

        :param account_id: player's account id
        :param char_id: character's db id
        :return:
        """
        self.storage.add(account_id, char_id)

    def remove_character(self, account_id, char_id):
        """
        Remove an character.

        :param account_id: player's account id
        :param char_id: character's db id
        :return:
        """
        self.storage.delete(account_id, char_id)

    def get_account_characters(self, account_id):
        """
        Get all characters of an account.
        :param account_id:
        :return:
        """
        return self.storage.load_category(account_id, {})
