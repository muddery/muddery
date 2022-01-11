"""
EventHandler handles all events. The handler sets on every object.
"""

import random
import weakref
from muddery.server.utils import defines
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.database.worlddata.event_data import EventData
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.server.utils.defines import EventType


class EventTrigger(object):
    """
    Every object has an event trigger. The event trigger works when this object acts with another object.
    """

    # available trigger types
    triggers = {
        # at attriving a room. trigger_obj: room_id
        EventType.EVENT_TRIGGER_ARRIVE: {
            "name": "On Arrive"
        },
        # caller kills one. trigger_obj: dead_one_id
        EventType.EVENT_TRIGGER_KILL: {
            "name": "On kill the Target"
        },
        # caller die. trigger_obj: killer_id
        EventType.EVENT_TRIGGER_DIE: {
            "name": "On Die"
        },
        # before traverse an exit. trigger_obj: exit_id
        EventType.EVENT_TRIGGER_TRAVERSE: {
            "name": "On Traverse An Exit"
        },
        # when a character finishes a dialogue sentence. trigger_obj: sentence_id
        EventType.EVENT_TRIGGER_DIALOGUE: {
            "name": "On Finish a Dialogue"
        }
    }

    def __init__(self, owner, object_key=None):
        """
        Initialize the handler.
        """
        self.owner = weakref.proxy(owner)

        # The owner can bypass all events.
        self.can_bypass = self.owner.is_staff()

    @classmethod
    def all_triggers(cls):
        """
        Get all event triggers.

        Returns:
            (list) all trigger's key.
        """
        return cls.triggers.keys()

    @classmethod
    def choice_all(cls):
        """
        Get all event triggers' types and names.
        """
        return [(key.value, "%s (%s)" % (value["name"], key.value)) for key, value in cls.triggers.items()]

    def trigger(self, event_type, obj_key="", obj=None):
        """
        Trigger an event.

        Args:
            event_type: (string) event's type.
            obj_key: (string) the event object's key.
            # todo: use get_element_key to get the object's key.

        Return:
            triggered: (boolean) if an event is triggered.
        """
        if self.can_bypass:
            return False

        # Query events.
        events = EventData.get_element_event(event_type.value, obj_key)
        if not events:
            return False

        # Get available events.
        candidates = [e for e in events if not self.owner.is_event_closed(e.key) and
                      STATEMENT_HANDLER.match_condition(e.condition, self.owner, obj)]

        triggered = False
        rand = random.random()
        for event in candidates:
            if event.multiple:
                if rand < event.odds:
                    func = EVENT_ACTION_SET.func(event.action)
                    if func:
                        func(event.key, self.owner, obj)
                    triggered = True
                rand = random.random()
            else:
                if rand < event.odds:
                    func = EVENT_ACTION_SET.func(event.action)
                    if func:
                        func(event.key, self.owner, obj)
                    triggered = True
                    break
                rand -= event.odds

        return triggered

    #########################
    #
    # Event triggers
    #
    #########################
    def at_character_move_in(self, location):
        """
        Called when a character moves in the event handler's owner, usually a room.
        """
        self.trigger(EventType.EVENT_TRIGGER_ARRIVE, location.get_element_key(), location)

    def at_character_move_out(self, location):
        """
        Called when a character moves out of a room.
        """
        # Remove room interval actions.
        """
        scripts = self.owner.scripts.all()
        for script in scripts:
            if script.is_element("SCRIPT_ROOM_INTERVAL"):
                script.stop()
        """

    def at_character_die(self):
        """
        Called when a character is killed.
        """
        self.trigger(EventType.EVENT_TRIGGER_DIE)

    def at_character_kill(self, opponent):
        """
        Called when a character kills another one.
        """
        # If has kill event.
        self.trigger(EventType.EVENT_TRIGGER_KILL, opponent.get_element_key(), opponent)

    def at_dialogue(self, dlg_key):
        """
        Called when a character finishes a dialogue.
        """
        triggered = self.trigger(EventType.EVENT_TRIGGER_DIALOGUE, dlg_key)
        return not triggered
