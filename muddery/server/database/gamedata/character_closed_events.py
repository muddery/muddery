
"""
Store object's element key data in memory.
"""

from muddery.server.database.gamedata.base_data import BaseData
from muddery.common.utils.singleton import Singleton


class CharacterClosedEvents(BaseData, Singleton):
    """
    The storage of all character's quest's objectives.
    """
    __table_name = "character_closed_events"
    __category_name = "character_id"
    __key_field = "event"
    __default_value_field = "event"

    def __init__(self):
        # data storage
        super(CharacterClosedEvents, self).__init__()
        self.storage = self.create_storage(self.__table_name, self.__category_name, self.__key_field, self.__default_value_field)

    async def get_character(self, character_id):
        """
        Get a character's events info.
        :param character_id:
        :return:
        """
        return await self.storage.load_category(character_id, {})

    async def has(self, character_id, event):
        """
        Get a character's event info.
        :param character_id: (int) character's id
        :param event: (string) event's key
        :return:
        """
        return await self.storage.has(character_id, event)

    async def add(self, character_id, event):
        """
        Add a new quest.
        :param character_id:
        :param event:
        :return:
        """
        await self.storage.add(character_id, event)

    async def remove_character(self, character_id):
        """
        Remove a character's all events.

        :param character_id:
        :return:
        """
        await self.storage.delete_category(character_id)

    async def remove(self, character_id, event):
        """
        Remove an event.

        :param character_id:
        :param event: (string) event's key
        :return:
        """
        await self.storage.delete(character_id, event)
