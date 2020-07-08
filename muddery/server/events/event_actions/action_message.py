"""
Event action.
"""

from muddery.server.events.base_interval_action import BaseIntervalAction
from muddery.server.dao.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _


class ActionMessage(BaseIntervalAction):
    """
    Attack a target.
    """
    key = "ACTION_MESSAGE"
    name = _("Message", category="event_actions")
    model_name = "action_message"
    repeatedly = True

    def func(self, event_key, character, obj):
        """
        Send a message to the character.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)

        # send messages
        for record in records:
            character.msg(record.message)
