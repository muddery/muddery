"""
Characters' combat.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.common.utils.singleton import Singleton


class CharacterCombat(BaseData, Singleton):
    """
    Player character's combat data.
    """
    __table_name = "character_combat"
    __category_name = None
    __key_field = "character_id"
    __default_value_field = "combat"

    def __init__(self):
        # data storage
        super(CharacterCombat, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def save(self, character_id, combat_id):
        """
        Set a combat.

        Args:
            character_id: (int) character's id.
            combat_id: (int) combat's id.
        """
        await self.storage.save("", character_id, combat_id)

    async def has(self, character_id):
        """
        Check if the character exists.

        Args:
            character_id: (int) character's id.
        """
        return await self.storage.has("", character_id)

    async def load(self, character_id, *default):
        """
        Get the combat's id of a character.

        Args:
            character_id: (int) character's id.
            default: (int) default value
        """
        return await self.storage.load("", character_id, *default)

    async def remove_character(self, character_id):
        """
        Remove all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        await self.storage.delete("", character_id)
