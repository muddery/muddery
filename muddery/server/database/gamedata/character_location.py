"""
Characters' combat.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.common.utils.singleton import Singleton


class CharacterLocation(BaseData, Singleton):
    """
    Player character's location.
    """
    __table_name = "character_location"
    __category_name = None
    __key_field = "char_id"
    __default_value_field = "location"

    def __init__(self):
        # data storage
        super(CharacterLocation, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def save(self, char_id, location):
        """
        Set a player character's location.

        Args:
            char_id: (int) player character's id.
            location: (string) location's key.
        """
        await self.storage.save("", char_id, location)

    async def load(self, char_id, *default):
        """
        Get the location of a player character.

        Args:
            char_id: (int) player character's id.
            default: (int) default value
        """
        return await self.storage.load("", char_id, *default)

    async def remove_character(self, char_id):
        """
        Remove a player character.

        Args:
            char_id: (number) player character's id.
        """
        await self.storage.delete("", char_id)
