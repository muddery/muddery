"""
All available event triggers.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.events.event_trigger import EventTrigger


class EventTriggerSet(object):
    """
    All available event triggers.
    """
    def all(self):
        """
        Get the processer responds to the request.
        """
        return EventTrigger.triggers


EVENT_TRIGGER_SET = EventTriggerSet()

