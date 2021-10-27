"""
Characters' skills.
"""

from django.conf import settings
from muddery.server.utils import utils


class CharacterSkills(object):
    """
    Player character's skills data, including which skills a player character has, skill's level and other data.
    """
    # data storage
    storage_class = utils.class_from_path(settings.DATABASE_ACCESS_OBJECT)
    storage = storage_class("character_skills", "character_id", "skill")

    @classmethod
    def save(cls, character_id, skill_key, data):
        """
        Set a skill.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
            data: (dict) data to save.
        """
        cls.storage.save(character_id, skill_key, data)

    @classmethod
    def has(cls, character_id, skill_key):
        """
        Check if the skill exists.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
        """
        return cls.storage.has(character_id, skill_key)

    @classmethod
    def load(cls, character_id, skill_key, **default):
        """
        Get the value of a skill.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
            default: (any or none) default value.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        return cls.storage.load(character_id, skill_key, **default)

    @classmethod
    def load_character(cls, character_id):
        """
        Get all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        return cls.storage.load_category(character_id, {})

    @classmethod
    def delete(cls, character_id, skill_key):
        """
        delete a skill of a character.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
        """
        cls.storage.delete(character_id, skill_key)

    @classmethod
    def remove_character(cls, character_id):
        """
        Remove all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        cls.storage.delete_category(character_id)
