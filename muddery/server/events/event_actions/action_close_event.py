"""
Event action.
"""

from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.database.dao.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _


class ActionCloseEvent(BaseEventAction):
    """
    Close events.
    """
    key = "ACTION_CLOSE_EVENT"
    name = _("Close an Event", category="event_actions")
    model_name = "action_close_event"
    repeatedly = False

    def func(self, event_key, character, obj):
        """
        Close an event.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)

        for record in records:
            # Close event.
            character.close_event(record.event)
