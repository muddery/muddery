"""
Characters' combat.
"""

import json, traceback
from django.conf import settings
from muddery.server.utils import utils
from muddery.server.utils.exception import MudderyError, ERR


class CharacterLocation(object):
    """
    Player character's location.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    storage = storage_class("character_location", "", "char_id", "location")

    @classmethod
    def save(cls, char_id, location):
        """
        Set a player character's location.

        Args:
            char_id: (int) player character's id.
            location: (string) location's key.
        """
        cls.storage.save("", char_id, location)

    @classmethod
    def load(cls, char_id, *default):
        """
        Get the location of a player character.

        Args:
            char_id: (int) player character's id.
            default: (int) default value
        """
        return cls.storage.load("", char_id, *default)

    @classmethod
    def remove_character(cls, char_id):
        """
        Remove a player character.

        Args:
            char_id: (number) player character's id.
        """
        cls.storage.delete("", char_id)
