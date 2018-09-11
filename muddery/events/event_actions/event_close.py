"""
Event action.
"""

import random
from django.apps import apps
from django.conf import settings
from muddery.events.base_event_action import BaseEventAction
from muddery.utils.localized_strings_handler import _


class EventClose(BaseEventAction):
    """
    Close an event.
    """
    key = "EVENT_CLOSE"
    name = _("Close")
    model_name = "event_closes"

    def func(self, event_key, character):
        """
        Close an event.

        Args:
            event_key: (string) event's key.
            character: (obj) relative character.
        """
        # get action data
        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        records = model_obj.objects.filter(event_key=event_key)

        for record in records:
            # Close event.
            character.close_event(record.event)
            return
