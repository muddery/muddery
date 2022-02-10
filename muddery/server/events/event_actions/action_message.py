"""
Event action.
"""

from muddery.server.events.base_interval_action import BaseIntervalAction
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.common.utils.utils import async_wait


class ActionMessage(BaseIntervalAction):
    """
    Show messages to the character.
    """
    key = "ACTION_MESSAGE"
    name = "Message"
    model_name = "action_message"
    repeatedly = True

    async def func(self, event_key, character, obj):
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
        if records:
            await async_wait([character.msg(r.message) for r in records])
