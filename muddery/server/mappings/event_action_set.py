"""
All available event actions.
"""

from muddery.common.utils.utils import classes_in_path
from muddery.common.utils.singleton import Singleton
from muddery.common.utils.utils import async_wait
from muddery.server.settings import SETTINGS
from muddery.server.utils.logger import logger
from muddery.server.events.base_event_action import BaseEventAction


class EventActionSet(Singleton):
    """
    All available event triggers.
    """
    def __init__(self):
        self.dict = {}

    async def load(self):
        """
        Add all event actions from the path.
        """
        # load classes
        for cls in classes_in_path(SETTINGS.PATH_EVENT_ACTION_BASE, BaseEventAction):
            key = cls.key
            if key:
                if key in self.dict:
                    logger.log_debug("Event action %s is replaced by %s." % (key, cls))
                action = cls()
                self.dict[key] = action

        await async_wait([item.init() for item in self.dict.values()])

    def get(self, key):
        """
        Get the event action.
        """
        return self.dict.get(key, None)

    def get_func(self, key):
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
