"""
All available event actions.
"""

from django.conf import settings
from muddery.server.utils.logger import logger
from muddery.server.utils.utils import classes_in_path
from muddery.server.events.base_event_action import BaseEventAction


class EventActionSet(object):
    """
    All available event triggers.
    """
    def __init__(self):
        self.dict = {}

    def load(self):
        """
        Add all event actions from the path.
        """
        # load classes
        for cls in classes_in_path(settings.PATH_EVENT_ACTION_BASE, BaseEventAction):
            key = cls.key
            if key:
                if key in self.dict:
                    logger.log_info("Event action %s is replaced by %s." % (key, cls))
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

    def choice_all(self):
        """
        Get all event types and names for form choice.
        """
        return [(key, "%s (%s)" % (value.name, key)) for key, value in self.dict.items()]

    def repeatedly(self):
        """
        Get all repeatedly event types.
        """
        return [key for key, value in self.dict.items() if value.repeatedly]

    def choice_repeatedly(self):
        """
        Get all repeatedly event types and names.
        """
        return [(key, "%s (%s)" % (value.name, key)) for key, value in self.dict.items() if value.repeatedly]


EVENT_ACTION_SET = EventActionSet()
EVENT_ACTION_SET.load()
