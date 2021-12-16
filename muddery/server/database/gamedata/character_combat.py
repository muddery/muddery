"""
Characters' combat.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class CharacterCombat(BaseData, Singleton):
    """
    Player character's combat data.
    """
    __table_name = "character_combat"
    __category_name = ""
    __key_field = "character_id"
    __default_value_field = "combat"

    def save(self, character_id, combat_id):
        """
        Set a combat.

        Args:
            character_id: (int) character's id.
            combat_id: (int) combat's id.
        """
        self.storage.save("", character_id, combat_id)

    def has(self, character_id):
        """
        Check if the character exists.

        Args:
            character_id: (int) character's id.
        """
        return self.storage.has("", character_id)

    def load(self, character_id, *default):
        """
        Get the combat's id of a character.

        Args:
            character_id: (int) character's id.
            default: (int) default value
        """
        return self.storage.load("", character_id, *default)

    def remove_character(self, character_id):
        """
        Remove all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        self.storage.delete("", character_id)
