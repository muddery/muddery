"""
All available event triggers.
"""

from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.events.event_trigger import EventTrigger


class EventTriggerSet(object):
    """
    All available event triggers.
    """
    def choice_all(self):
        """
        Get the processor responds to the request for form choice.
        """
        return EventTrigger.choice_all()


EVENT_TRIGGER_SET = EventTriggerSet()

