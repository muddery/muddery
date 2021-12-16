"""
Characters' skills.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class CharacterSkills(BaseData, Singleton):
    """
    Player character's skills data, including which skills a player character has, skill's level and other data.
    """
    __table_name = "character_skills"
    __category_name = "character_id"
    __key_field = "skill"
    __default_value_field = ""

    def save(self, character_id, skill_key, data):
        """
        Set a skill.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
            data: (dict) data to save.
        """
        self.storage.save(character_id, skill_key, data)

    def has(self, character_id, skill_key):
        """
        Check if the skill exists.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
        """
        return self.storage.has(character_id, skill_key)

    def load(self, character_id, skill_key, **default):
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
        return self.storage.load(character_id, skill_key, **default)

    def load_character(self, character_id):
        """
        Get all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        return self.storage.load_category(character_id, {})

    def delete(self, character_id, skill_key):
        """
        delete a skill of a character.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
        """
        self.storage.delete(character_id, skill_key)

    def remove_character(self, character_id):
        """
        Remove all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        self.storage.delete_category(character_id)
