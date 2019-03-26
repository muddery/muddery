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
    def __init__(self, *args, **kwargs):
        super(ScriptRoomInterval, self).__init__(*args, **kwargs)

        # Set default values.
        self.room = None
        self.event_key = ""
        self.action = ""
        self.begin_message = ""
        self.end_message = ""

    def at_script_creation(self):
        self.key = "room_interval_script"
        self.persistent = True

    def set_action(self, room, event_key, action, begin_message, end_message):
        """
        Set action data.

        Args:
            event: (string) event's key.
            action: (string) action's key.
        """
        self.room = room
        self.event_key = event_key
        self.action = action
        self.begin_message = begin_message
        self.end_message = end_message

    def at_start(self):
        """
        Called every time the script is started.
        """
        if self.begin_message:
            if self.obj:
                self.obj.msg(self.begin_message)

    def at_repeat(self):
        """
        Trigger events.
        """
        if not self.obj:
            self.stop()
            return

        if not self.room:
            # The room does not exist.
            self.obj.scripts.delete(self)
            return

        if self.obj.location != self.room:
            # The character has left the room.
            self.obj.scripts.delete(self)
            return

        # Do actions.
        func = EVENT_ACTION_SET.func(self.action)
        if func:
            func(self.event_key, self.obj, self.room)

    def at_stop(self):
        """
        Called every time the script is started.
        """
        if self.end_message:
            if self.obj:
                self.obj.msg(self.end_message)
