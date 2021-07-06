"""
Event action.
"""

from evennia import create_script
from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _


class ActionRoomInterval(BaseEventAction):
    """
    Triggers an event in a room at interval.
    """
    key = "ACTION_ROOM_INTERVAL"
    name = _("Room Interval Action", category="event_actions")
    model_name = "action_room_interval"
    repeatedly = False

    def func(self, event_key, character, obj):
        """
        Triggers an event at interval.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)
