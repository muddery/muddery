"""
Event action.
"""

from __future__ import print_function

import random
from django.apps import apps
from django.conf import settings
from muddery.events.base_event_action import BaseEventAction
from muddery.utils.localized_strings_handler import _


class ActionGetObjects(BaseEventAction):
    """
    Attack a target.
    """
    key = "ACTION_GET_OBJECTS"
    name = _("Message")
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
        # get action data
        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        records = model_obj.objects.filter(event_key=event_key)

        # get object list
        obj_list = []
        for record in records:
            rand = random.random()
            if rand < record.odds:
                obj_list.append({"object": record.object,
                                 "number": record.number})

        result = character.receive_objects(obj_list, mute=True)

        accepted = ""
        for name in result["accepted_names"]:
            if accepted:
                accepted += ", "
            accepted += name + " " + str(result["accepted_names"][name])

        rejected = ""
        for name in result["reject_reason"]:
            if rejected:
                rejected += ", "
            rejected += name + " " + result["reject_reason"][name]

        if accepted:
            message = _("Get") + " " + accepted
            character.msg(message)

        if rejected:
            message = _("Can not get") + " " + rejected
            character.msg(message)
