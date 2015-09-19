"""
EventHandler
"""

import re
from muddery.utils import defines
from muddery.utils.builder import build_object
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger


class EventHandler(object):
    """
    """
    def __init__(self, owner):
        """
        Initialize handler
        """
        self.owner = owner
        self.events = {}

        event_records = []
        model_events = get_model(settings.WORLD_DATA_APP, settings.EVENT_DATA)
        if model_events:
            # Get records.
            event_records = model_events.objects.filter(key=owner.get_info_key)

        for event_record in event_records:
            if not event_record.trigger in self.events:
                self.events[event_record.trigger] = []
            
            event = {"type": event_record.type}
            if event_record.type == defines.EVENT_ATTACK:
                event["function"] = self.do_attack

            self.events[event_record.trigger].append(event)


    def at_character_move_in(self, location):
        """
        """
        if defines.EVENT_TRIGGER_ARRIVE in self.events:
            for event in self.events[defines.EVENT_TRIGGER_ARRIVE]:
                event["function"]()


    def at_character_move_out(self):
        """
        """
        pass


    def do_attack(self):
        """
        """
        print "do_attack"
