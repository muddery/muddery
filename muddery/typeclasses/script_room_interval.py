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


class ScriptRoomInterval(DefaultScript):
    """
    This script triggers an event in a room at intervals.
    """
    def __init__(self, room, target, interval):
        self.interval = interval
        self.delay_start = True

        self.room = room
        self.target = target

    def at_repeat(self):
        """
        Trigger events.
        """
        if not self.room:
            self.target.scripts.delete(self)
            return

        if self.targrt not in self.room:
            # The target has left the room.
            self.target.scripts.delete(self)
            return

        # Trigger the event.
        self.room.event.trigger(defines.EVENT_TRIGGER_ROOM_INTERVAL, self.target, self.room)
