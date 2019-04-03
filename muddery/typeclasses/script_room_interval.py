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
    def at_script_creation(self):
        # Set default data.
        if not self.attributes.has("room"):
            self.db.room = None
        if not self.attributes.has("event_key"):
            self.db.event_key = ""
        if not self.attributes.has("action"):
            self.db.action = ""
        if not self.attributes.has("begin_message"):
            self.db.begin_message = ""
        if not self.attributes.has("end_message"):
            self.db.end_message = ""

    def set_action(self, room, event_key, action, begin_message, end_message):
        """
        Set action data.

        Args:
            event: (string) event's key.
            action: (string) action's key.
        """
        self.db.room = room
        self.db.event_key = event_key
        self.db.action = action
        self.db.begin_message = begin_message
        self.db.end_message = end_message

    def at_start(self):
        """
        Called every time the script is started.
        """
        if self.db.begin_message:
            if self.obj:
                self.obj.msg(self.db.begin_message)

    def at_repeat(self):
        """
        Trigger events.
        """
        if not self.obj.location:
            # The character's location is empty (maybe just login).
            return

        if self.obj.location != self.db.room:
            # The character has left the room.
            self.obj.scripts.delete(self)
            return

        # Do actions.
        func = EVENT_ACTION_SET.func(self.db.action)
        if func:
            func(self.db.event_key, self.obj, self.db.room)

    def at_stop(self):
        """
        Called every time the script is started.
        """
        if self.db.end_message:
            if self.obj:
                self.obj.msg(self.db.end_message)
