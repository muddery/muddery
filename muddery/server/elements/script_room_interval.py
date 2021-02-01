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
from muddery.server.elements.scripts import MudderyScript
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.server.dao.worlddata import WorldData


class ScriptRoomInterval(MudderyScript):
    """
    This script triggers an event in a room at intervals.
    """
    def at_init(self):
        """
        Load the script's data.
        """
        self.event_key = self.state.load("event_key", "")
        self.action = self.state.load("action", "")
        self.room = self.state.load("room", "")

        self.offline = False
        self.begin_message = ""
        self.end_message = ""

        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=self.event_key, action=self.action)
        if len(records) > 0:
            self.offline = records[0].offline
            self.begin_message = records[0].begin_message
            self.end_message = records[0].end_message

    def set_action(self, room, event_key, action):
        """
        Set action data.

        Args:
            room: (string) room's key.
            event_key: (string) event's key.
            action: (string) action's key.
        """
        self.event_key = event_key
        self.action = action

        self.state.saves({
            "room": room,
            "event_key": event_key,
            "action": action,
            "last_trigger_time": 0,
        })

        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=self.event_key, action=self.action)
        if len(records) > 0:
            self.offline = records[0].offline
            self.begin_message = records[0].begin_message
            self.end_message = records[0].end_message

    def at_start(self):
        """
        Called every time the script is started.
        """
        # The script will be unpaused when the server restarts. So pause it if the character is no online now.
        if self.begin_message:
            if self.obj:
                self.obj.msg(self.begin_message)

        # Offline intervals.
        if self.offline:
            last_time = self.state.load("last_trigger_time", 0)
            if last_time:
                current_time = time.time()
                times = int((current_time - last_time) / self.interval)
                if times > 0:
                    self.state.save("last_trigger_time", current_time)
                    action = EVENT_ACTION_SET.get(self.action)
                    if action and hasattr(action, "offline_func"):
                        action.offline_func(self.event_key, self.obj, self.room, times)

    def at_repeat(self):
        """
        Trigger events.
        """
        if not self.obj.location:
            # The character's location is empty (maybe just login).
            return

        if self.obj.location != self.room:
            # The character has left the room.
            self.obj.scripts.delete(self)
            return

        # Do actions.
        if self.offline:
            self.state.save("last_trigger_time", time.time())
        func = EVENT_ACTION_SET.func(self.action)
        if func:
            func(self.event_key, self.obj, self.room)

    def at_stop(self):
        """
        Called every time the script is stopped.
        """
        if self.end_message:
            if self.obj:
                self.obj.msg(self.end_message)
