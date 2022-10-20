"""
Event action.
"""

from muddery.server.events.base_interval_action import BaseIntervalAction
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.common.utils.utils import async_gather


class ActionAddRelationship(BaseIntervalAction):
    """
    Set the relation between the character and the element.
    """
    key = "ACTION_ADD_RELATION"
    name = "Add Relation"
    model_name = "action_inc_relation"
    repeatedly = True

    async def func(self, event_key, character, obj):
        """
        Add the relation between the character and the element by the value

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)

        # send messages
        if records:
            return await async_gather([character.increase_relation(r.element_type, r.element_key, r.value) for r in records])
