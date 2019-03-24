"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

from muddery.utils import defines
from evennia.scripts.scripts import DefaultScript
from muddery.mappings.event_action_set import EVENT_ACTION_SET


class ScriptRoomInterval(DefaultScript):
    """
    This script triggers an event in a room at intervals.
    """
    def __init__(self, room, interval, event_key, actions):
        """
        Args:
            room: (obj) the room that the character is in.
            interval: (number) the interval
            event_key: (string) the key of the event.
            actions: (list) a list of actions
        """
        super(ScriptRoomInterval, self).__init__()

        self.interval = interval
        self.delay_start = True

        self.room = room
        self.event_key = event_key
        self.actions = actions

    def at_repeat(self):
        """
        Trigger events.
        """
        if not self.obj:
            self.stop()
            return

        if self.obj.location != self.room:
            # The character has left the room.
            self.obj.scripts.delete(self)
            return

        # Do actions.
        for action in self.actions:
            func = EVENT_ACTION_SET.func(action)
            if func:
                func(self.event_key, self.obj, self.room)
