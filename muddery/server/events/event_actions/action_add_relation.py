"""
Event action.
"""

import traceback
from muddery.server.events.base_interval_action import BaseIntervalAction
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.utils.logger import logger


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
        for record in records:
            try:
                await character.set_relationship(record.element_type, record.element_key, record.value)
            except Exception as e:
                traceback.print_exc()
                logger.log_err("Can not set relationship %s %s" % (type(e).__name__, e))
                pass
