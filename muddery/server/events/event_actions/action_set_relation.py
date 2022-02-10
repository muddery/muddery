"""
Event action.
"""

from muddery.server.events.base_interval_action import BaseIntervalAction
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.common.utils.utils import async_wait


class ActionSetRelationship(BaseIntervalAction):
    """
    Set the relation between the character and the element.
    """
    key = "ACTION_SET_RELATION"
    name = "Set Relation"
    model_name = "action_set_relation"
    repeatedly = True

    async def func(self, event_key, character, obj):
        """
        Set the relation between the character and the element.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)

        # send messages
        if records:
            await async_wait([character.set_relationship(r.element_type, r.element_key, r.value) for r in records])

