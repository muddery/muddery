"""
EventHandler handles all events. The handler sets on every object.
"""

import random
from muddery.utils import defines
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils import utils
from muddery.worlddata.dao import event_mapper
from muddery.mappings.event_action_set import EVENT_ACTION_SET
from django.conf import settings
from django.apps import apps
from evennia.utils import logger


PERMISSION_BYPASS_EVENTS = {perm.lower() for perm in settings.PERMISSION_BYPASS_EVENTS}


class EventTrigger(object):
    """
    Trigger an event.
    """

    # available trigger types
    triggers = [
        defines.EVENT_TRIGGER_ARRIVE,   # at attriving a room. object: room_id
        defines.EVENT_TRIGGER_KILL,     # caller kills one. object: dead_one_id
        defines.EVENT_TRIGGER_DIE,      # caller die. object: killer_id
        defines.EVENT_TRIGGER_TRAVERSE, # before traverse an exit. object: exit_id
        defines.EVENT_TRIGGER_ACTION,   # when a character act to an object. object_id: 
    ]

    def __init__(self, owner):
        """
        Initialize the handler.
        """
        self.owner = owner
        self.events = {}

        object_key = owner.get_data_key()

        # Load events.
        event_records = event_mapper.get_object_event(object_key)

        for record in event_records:
            event = {}

            # Set data.
            event_type = record.type
            trigger_type = record.trigger_type

            for field in record._meta.fields:
                event[field.name] = record.serializable_value(field.name)
            event["type"] = event_type

            # Set additional data.
            event_additional = event_mapper.get_event_additional_data(event_type, event["key"])
            if event_additional:
                event.update(event_additional)

            if not trigger_type in self.events:
                self.events[trigger_type] = []
            self.events[trigger_type].append(event)

    def can_bypass(self, character):
        """
        If the character can bypass the event.
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

        event_list = self.events[event_type]
        candidates = [e for e in event_list if STATEMENT_HANDLER.match_condition(e["condition"], character, obj)]

        rand = random.random()
        for event in candidates:
            if rand < event["odds"]:
                func = EVENT_ACTION_SET.get(event["type"])
                if func:
                    func(event, character)
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
        pass

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
                self.trigger(defines.EVENT_TRIGGER_DIE, killer, self.owner)

    def at_character_traverse(self, character):
        """
        Called before a character traverses an exit.
        If returns true, the character can pass the exit, else the character can not pass the exit.
        """
        triggered = self.trigger(defines.EVENT_TRIGGER_TRAVERSE, character, self.owner)
        return not triggered
        
    def at_action(self, character, obj):
        """
        Called when a character act to an object.
        """
        triggered = self.trigger(defines.EVENT_TRIGGER_ACTION, character, self.owner)
        return not triggered

