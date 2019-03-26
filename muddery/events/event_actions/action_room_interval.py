"""
Event action.
"""

from __future__ import print_function

from django.apps import apps
from django.conf import settings
from evennia import create_script
from muddery.events.base_event_action import BaseEventAction
from muddery.utils.localized_strings_handler import _
from muddery.typeclasses.script_room_interval import ScriptRoomInterval


class ActionRoomInterval(BaseEventAction):
    """
    Triggers an event at interval.
    """
    key = "ACTION_ROOM_INTERVAL"
    name = _("Triggers an event in a room at interval.")
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
        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        records = model_obj.objects.filter(event_key=event_key)

        # Add actions.
        for record in records:
            script = create_script(ScriptRoomInterval,
                                   key=event_key,
                                   interval=record.interval,
                                   autostart=False,
                                   start_delay=True,
                                   obj=character)
            script.set_action(obj, event_key, record.action, record.begin_message, record.end_message)
            script.start()
