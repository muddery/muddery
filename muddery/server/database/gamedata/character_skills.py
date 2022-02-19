"""
Characters' skills.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.common.utils.singleton import Singleton


class CharacterSkills(BaseData, Singleton):
    """
    Player character's skills data, including which skills a player character has, skill's level and other data.
    """
    __table_name = "character_skills"
    __category_name = "character_id"
    __key_field = "skill"
    __default_value_field = None

    def __init__(self):
        # data storage
        super(CharacterSkills, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def save(self, character_id, skill_key, data):
        """
        Set a skill.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
            data: (dict) data to save.
        """
        await self.storage.save(character_id, skill_key, data)

    async def has(self, character_id, skill_key):
        """
        Check if the skill exists.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
        """
        return await self.storage.has(character_id, skill_key)

    async def load(self, character_id, skill_key, *default):
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
        return await self.storage.load(character_id, skill_key, *default)

    async def load_character(self, character_id):
        """
        Get all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        return await self.storage.load_category(character_id, {})

    async def delete(self, character_id, skill_key):
        """
        delete a skill of a character.

        Args:
            character_id: (number) character's id.
            skill_key: (string) skill's key.
        """
        await self.storage.delete(character_id, skill_key)

    async def remove_character(self, character_id):
        """
        Remove all skills of a character.

        Args:
            character_id: (number) character's id.
        """
        await self.storage.delete_category(character_id)
