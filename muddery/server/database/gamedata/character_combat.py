"""
Characters' combat.
"""

from django.conf import settings
from muddery.server.utils import utils


class CharacterCombat(object):
    """
    Player character's combat data.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    storage = storage_class("character_combat", "", "character_id", "combat")

    @classmethod
    def save(cls, character_id, combat_id):
        """
        Set a combat.

        Args:
            character_id: (int) character's id.
            combat_id: (int) combat's id.
        """
        cls.storage.save("", character_id, combat_id)

    @classmethod
    def has(cls, character_id):
        """
        Check if the character exists.

        Args:
            character_id: (int) character's id.
        """
        return cls.storage.has("", character_id)

    @classmethod
    def load(cls, character_id, *default):
        """
        Get the combat's id of a character.

        Args:
            character_id: (int) character's id.
            default: (int) default value
        """
        return cls.storage.load("", character_id, *default)

    @classmethod
    def remove_character(cls, character_id):
        """
        Remove all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        cls.storage.delete("", character_id)
