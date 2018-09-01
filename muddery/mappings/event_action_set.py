"""
All available event actions.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.utils.utils import classes_in_path
from muddery.events.base_event_action import BaseEventAction


class EventActionSet(object):
    """
    All available event triggers.
    """
    def __init__(self):
        self.dict = {}
        self.load()

    def load(self):
        """
        Add all event actions from the path.
        """
        # load classes
        for cls in classes_in_path(settings.PATH_EVENT_ACTION_BASE, BaseEventAction):
            key = cls.key

            if self.dict.has_key(key):
                logger.log_infomsg("Event action %s is replaced by %s." % (key, cls))

            self.dict[key] = cls()

    def get(self, key):
        """
        Get the event action.
        """
        return self.dict.get(key, None)

    def func(self, key):
        """
        Get the function of the event action.
        """
        action = self.dict.get(key, None)
        if action:
            return action.func

    def all(self):
        """
        Get all event types.
        """
        return self.dict.keys()


EVENT_ACTION_SET = EventActionSet()
