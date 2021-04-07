"""
Characters' combat.
"""

import json, traceback
from django.conf import settings
from muddery.server.utils import utils
from muddery.server.utils.exception import MudderyError, ERR


class CharacterCombat(object):
    """
    Player character's combat data.
    """
    def __init__(self, model_name):
        # db model
        storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
        self.storage = storage_class(model_name, "", "character_id", "combat")

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

    def remove(self, character_id):
        """
        Remove all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        self.storage.delete("", character_id)


CHARACTER_COMBAT = CharacterCombat("character_combat")
