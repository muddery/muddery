"""
The base class of interval event actions which can be triggered at intervals.
"""

from muddery.events.base_event_action import BaseEventAction


class BaseIntervalAction(BaseEventAction):
    """
    The base class of interval event actions which can be triggered at intervals.
    """
    repeatedly = True

    def offline_func(self, event_key, character, obj, times):
        """
        Event action's function when the character is offline.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
            times: (number) event triggered times when the player is offline.
        """
        pass
