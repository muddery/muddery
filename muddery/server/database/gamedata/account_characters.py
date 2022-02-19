
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.common.utils.singleton import Singleton


class AccountCharacters(BaseData, Singleton):
    """
    The storage of account's characters.
    """
    __table_name = "account_characters"
    __category_name = "account_id"
    __key_field = "char_id"
    __default_value_field = None

    def __init__(self):
        # data storage
        super(AccountCharacters, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def add(self, account_id, char_id):
        """
        Add a new player character.

        :param account_id: player's account id
        :param char_id: character's db id
        :return:
        """
        await self.storage.add(account_id, char_id)

    async def remove_character(self, account_id, char_id):
        """
        Remove an character.

        :param account_id: player's account id
        :param char_id: character's db id
        :return:
        """
        await self.storage.delete(account_id, char_id)

    async def get_account_characters(self, account_id):
        """
        Get all characters of an account.
        :param account_id:
        :return:
        """
        return await self.storage.load_category(account_id, {})
