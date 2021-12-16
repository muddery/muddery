"""
Event action.
"""

import random
from muddery.server.events.base_interval_action import BaseIntervalAction
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.utils.loot_handler import LootHandler
from muddery.server.utils.localized_strings_handler import _


class ActionGetObjects(BaseIntervalAction):
    """
    Get objects.
    """
    key = "ACTION_GET_OBJECTS"
    name = "Get Objects"
    model_name = "action_get_objects"
    repeatedly = True

    def func(self, event_key, character, obj):
        """
        Add objects to the character.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        self.get_object(event_key, character, 1)

    def get_object(self, event_key, character, times):
        """
        The character get objects.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            times: (number) event triggered times.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)

        # get object list
        loot_handler = LootHandler(records)
        obj_list = loot_handler.get_obj_list(character, times)
        get_objects = character.receive_objects(obj_list, mute=True)

        if get_objects:
            msg_templates = {item["object_key"]: item["message"] for item in obj_list}
            message = ""
            for item in get_objects:
                if message:
                    message += ", "

                template = msg_templates[item["key"]]
                if template:
                    try:
                        message += template % item["number"]
                    except Exception as e:
                        message += template
                else:
                    message += _("Get") + " " + item["name"] + " " + str(item["number"])

            character.msg({"msg": message})
