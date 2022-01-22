"""
The relationship between players and elements
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.server.utils.singleton import Singleton


class CharacterRelationships(BaseData, Singleton):
    """
    Player character's skills data, including which skills a player character has, skill's level and other data.
    """
    __table_name = "character_relationships"
    __category_name = "character_id"
    __key_field = "element"
    __default_value_field = "relationship"

    def __init__(self):
        # data storage
        super(CharacterRelationships, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def save(self, character_id: int, element_type: str, element_key: str, relationship: str) -> None:
        """
        Set a relationship.

        Args:
            character_id: (int) character's id.
            element_type: (string) the element's type.
            element_key: (string) the element's key.
            relationship: (int) their relationship
        """
        element = "%s:%s" % (element_type, element_key)
        await self.storage.save(character_id, element, relationship)

    async def add(self, character_id: int, element_type: str, element_key: str, value: int) -> None:
        """
        Get the value of a relationship.

        Args:
            character_id: (int) character's id.
            element_type: (string) the element's type.
            element_key: (string) the element's key.
            value: (int) value to add.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        element = "%s:%s" % (element_type, element_key)
        with self.storage.transaction():
            relationship = await self.storage.load(character_id, element, for_update=True)
            relationship += value
            await self.storage.save(character_id, element, relationship)

    async def has(self, character_id: int, element_type: str, element_key: str) -> bool:
        """
        Check if the relationship exists.

        Args:
            character_id: (int) character's id.
            element_type: (string) the element's type.
            element_key: (string) the element's key.
        """
        element = "%s:%s" % (element_type, element_key)
        return await self.storage.has(character_id, element)

    async def load(self, character_id: int, element_type: str, element_key: str, *default):
        """
        Get the value of a relationship.

        Args:
            character_id: (int) character's id.
            element_type: (string) the element's type.
            element_key: (string) the element's key.
            default: (any or none) default value.

        Raises:
            KeyError: If `raise_exception` is set and no matching Attribute
                was found matching `key` and no default value set.
        """
        element = "%s:%s" % (element_type, element_key)
        return await self.storage.load(character_id, element, *default)

    async def delete(self, character_id: int, element_type: str, element_key: str):
        """
        delete a relationship.

        Args:
            character_id: (int) character's id.
            element_type: (string) the element's type.
            element_key: (string) the element's key.
        """
        element = "%s:%s" % (element_type, element_key)
        await self.storage.delete(character_id, element)

    async def remove_character(self, character_id):
        """
        Remove all relationships of a character.

        Args:
            character_id: (number) character's id.
        """
        await self.storage.delete_category(character_id)
