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

import time
from muddery.server.typeclasses.scripts import MudderyScript
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET


class ScriptRoomInterval(MudderyScript):
    """
    This script triggers an event in a room at intervals.
    """
    def at_script_creation(self):
        # Set default data.
        if not self.states_handler.has("room"):
            self.state.room = None
        if not self.states_handler.has("event_key"):
            self.state.event_key = ""
        if not self.states_handler.has("action"):
            self.state.action = ""
        if not self.states_handler.has("begin_message"):
            self.state.begin_message = ""
        if not self.states_handler.has("end_message"):
            self.state.end_message = ""
        if not self.states_handler.has("offline"):
            self.state.offline = False
        if not self.states_handler.has("last_trigger_time"):
            self.state.last_trigger_time = 0

    def set_action(self, room, event_key, action, offline, begin_message, end_message):
        """
        Set action data.

        Args:
            event: (string) event's key.
            action: (string) action's key.
        """
        self.state.room = room
        self.state.event_key = event_key
        self.state.action = action
        self.state.begin_message = begin_message
        self.state.end_message = end_message
        self.state.offline = offline
        self.state.last_trigger_time = 0

    def at_start(self):
        """
        Called every time the script is started.
        """
        # The script will be unpaused when the server restarts. So pause it if the character is no online now.
        if self.state.begin_message:
            if self.obj:
                self.obj.msg(self.state.begin_message)

        # Offline intervals.
        if self.state.offline:
            last_time = self.state.last_trigger_time
            if last_time:
                current_time = time.time()
                times = int((current_time - last_time) / self.interval)
                if times > 0:
                    self.state.last_trigger_time = current_time
                    action = EVENT_ACTION_SET.get(self.state.action)
                    if action and hasattr(action, "offline_func"):
                        action.offline_func(self.state.event_key, self.obj, self.state.room, times)

    def at_repeat(self):
        """
        Trigger events.
        """
        if not self.obj.location:
            # The character's location is empty (maybe just login).
            return

        if self.obj.location != self.state.room:
            # The character has left the room.
            self.obj.scripts.delete(self)
            return

        # Do actions.
        if self.state.offline:
            self.state.last_trigger_time = time.time()
        func = EVENT_ACTION_SET.func(self.state.action)
        if func:
            func(self.state.event_key, self.obj, self.state.room)

    def at_stop(self):
        """
        Called every time the script is stopped.
        """
        if self.state.end_message:
            if self.obj:
                self.obj.msg(self.state.end_message)
