"""
Event action.
"""

import random
from django.apps import apps
from django.conf import settings
from muddery.events.base_interval_action import BaseIntervalAction
from muddery.utils.localized_strings_handler import _


class ActionGetObjects(BaseIntervalAction):
    """
    Get objects.
    """
    key = "ACTION_GET_OBJECTS"
    name = _("Get Objects", category="event_actions")
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

    def offline_func(self, event_key, character, obj, times):
        """
        Event action's function when the character is offline.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
            times: (number) event triggered times when the player is offline.
        """
        self.get_object(event_key, character, times)

    def get_object(self, event_key, character, times):
        """
        The character get objects.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            times: (number) event triggered times.
        """
        # get action data
        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        records = model_obj.objects.filter(event_key=event_key)

        # get object list
        obj_list = []
        for record in records:
            rand = random.random()
            if rand < record.odds:
                obj_list.append({"object": record.object,
                                 "number": record.number * times})

        objects = character.receive_objects(obj_list, mute=True)

        accepted = ""
        for item in objects:
            if accepted:
                accepted += ", "
            accepted += item["name"] + " " + str(item["number"])

        if accepted:
            message = _("Get") + " " + accepted
            character.msg(message)
