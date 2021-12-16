"""
Characters' combat.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class CharacterLocation(BaseData, Singleton):
    """
    Player character's location.
    """
    __table_name = "character_location"
    __category_name = ""
    __key_field = "char_id"
    __default_value_field = "location"

    def save(self, char_id, location):
        """
        Set a player character's location.

        Args:
            char_id: (int) player character's id.
            location: (string) location's key.
        """
        self.storage.save("", char_id, location)

    def load(self, char_id, *default):
        """
        Get the location of a player character.

        Args:
            char_id: (int) player character's id.
            default: (int) default value
        """
        return self.storage.load("", char_id, *default)

    def remove_character(self, char_id):
        """
        Remove a player character.

        Args:
            char_id: (number) player character's id.
        """
        self.storage.delete("", char_id)
