"""
EventHandler handles all events. The handler sets on every object.
"""

from __future__ import print_function

import random
from muddery.utils import defines
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils import utils
from muddery.worlddata.dao import event_mapper
from muddery.mappings.event_action_set import EVENT_ACTION_SET
from django.conf import settings
from django.apps import apps
from evennia.utils import logger
from muddery.typeclasses.script_room_interval import ScriptRoomInterval
from muddery.utils.localized_strings_handler import _


PERMISSION_BYPASS_EVENTS = {perm.lower() for perm in settings.PERMISSION_BYPASS_EVENTS}


class EventTrigger(object):
    """
    Every object has an event trigger. The event trigger works when this object acts with another object.
    """

    # available trigger types
    triggers = {
        # at attriving a room. trigger_obj: room_id
        defines.EVENT_TRIGGER_ARRIVE: {
            "name": _("On Arrive", category="event_triggers")
        },
        # caller kills one. trigger_obj: dead_one_id
        defines.EVENT_TRIGGER_KILL: {
            "name": _("On kill the Target", category="event_triggers")
        },
        # caller die. trigger_obj: killer_id
        defines.EVENT_TRIGGER_DIE: {
            "name": _("On Die", category="event_triggers")
        },
        # before traverse an exit. trigger_obj: exit_id
        defines.EVENT_TRIGGER_TRAVERSE: {
            "name": _("On Traverse An Exit", category="event_triggers")
        },
        # when a character finishes a dialogue sentence. trigger_obj: sentence_id
        defines.EVENT_TRIGGER_SENTENCE: {
            "name": _("On Finish a Sentence", category="event_triggers")
        }
    }

    def __init__(self, owner, object_key=None):
        """
        Initialize the handler.
        """
        self.owner = owner
        self.events = {}

        if not object_key:
            object_key = owner.get_data_key()

        # Load events.
        event_records = event_mapper.get_object_event(object_key)

        for record in event_records:
            event = {}

            # Set data.
            event_action = record.action
            trigger_type = record.trigger_type

            for field in record._meta.fields:
                event[field.name] = record.serializable_value(field.name)
            event["action"] = event_action

            if not trigger_type in self.events:
                self.events[trigger_type] = []
            self.events[trigger_type].append(event)

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
        return [(key, "%s (%s)" % (value["name"], key)) for key, value in cls.triggers.items()]

    def get_events(self):
        """
        If this event has specified action, returns True.
        """
        return self.events

    def can_bypass(self, character):
        """
        If the character can bypass the event, returns True.
        """
        if not character:
            return False

        if character.account:
            if character.account.is_superuser:
                # superusers can bypass events
                return True
            for perm in character.account.permissions.all():
                if perm in PERMISSION_BYPASS_EVENTS:
                    # has permission to bypass events
                    return True

    def trigger(self, event_type, character, obj):
        """
        Trigger an event.

        Args:
            event_type: (string) event's type.
            character: (object) the character who trigger this event.
            obj: (object) the event object.

        Return:
            triggered: (boolean) if an event is triggered.
        """
        if not character:
            return False

        if self.can_bypass(character):
            return False

        if event_type not in self.events:
            return False

        # Get all event's of this type.
        event_list = self.events[event_type]

        candidates = [e for e in event_list
                         if not character.is_event_closed(e["key"]) and
                             STATEMENT_HANDLER.match_condition(e["condition"], character, obj)]

        rand = random.random()
        for event in candidates:
            if rand < event["odds"]:
                func = EVENT_ACTION_SET.func(event["action"])
                if func:
                    func(event["key"], character, obj)
                return True
            rand -= event["odds"]

    #########################
    #
    # Event triggers
    #
    #########################
    def at_character_move_in(self, character):
        """
        Called when a character moves in the event handler's owner, usually a room.
        """
        self.trigger(defines.EVENT_TRIGGER_ARRIVE, character, self.owner)

    def at_character_move_out(self, character):
        """
        Called when a character moves out of a room.
        """
        # Remove room interval actions.
        scripts = character.scripts.all()
        for script in scripts:
            if script.is_typeclass(ScriptRoomInterval, exact=False):
                script.stop()

    def at_character_die(self):
        """
        Called when a character is killed.
        """
        self.trigger(defines.EVENT_TRIGGER_DIE, self.owner, None)

    def at_character_kill(self, killers):
        """
        Called when a character kills others.
        This event is set on the character who is killed, and take effect on the killer!
        """
        if defines.EVENT_TRIGGER_KILL in self.events:
            # If has kill event.
            for killer in killers:
                self.trigger(defines.EVENT_TRIGGER_KILL, killer, self.owner)

    def at_character_traverse(self, character):
        """
        Called before a character traverses an exit.
        If returns true, the character can pass the exit, else the character can not pass the exit.
        """
        triggered = self.trigger(defines.EVENT_TRIGGER_TRAVERSE, character, self.owner)
        return not triggered

    def at_sentence(self, character, obj):
        """
        Called when a character finishes a dialogue sentence.
        """
        triggered = self.trigger(defines.EVENT_TRIGGER_SENTENCE, character, obj)
