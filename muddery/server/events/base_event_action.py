"""
Event action's base class.
"""

from muddery.server.settings import SETTINGS
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.worldeditor.database.db_manager import DBManager


class BaseEventAction(object):
    """
    Event action's base class.
    """
    # action's key
    key = ""

    # action's readable name
    name = ""

    # action's additional data table
    model_name = ""

    # action's data model
    __model__ = None

    # this action can be called repeatedly in an event
    repeatedly = False

    @classmethod
    def model(cls):
        """
        Get the action's data model.
        """
        if cls.__model__:
            return cls.__model__

        cls.__model__ = DBManager.inst().get_model(SETTINGS.WORLD_DATA_APP, cls.model_name)
        return cls.__model__

    async def func(self, event_key, character, obj):
        """
        Event action's function.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        pass

    def get_event_data(self, event_key):
        """
        Query all actions of an event.

        Args:
            event_key: (string)event's key.
        """
        if not self.model_name:
            return

        return WorldData.get_table_data(self.model_name, event_key=event_key)
