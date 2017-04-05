"""
EventHandler handles all events. The handler sets on every object.
"""

import random
from muddery.utils import defines
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils import utils
from muddery.worlddata.data_sets import DATA_SETS
from django.conf import settings
from django.apps import apps
from evennia.utils import logger


PERMISSION_BYPASS_EVENTS = {perm.lower() for perm in settings.PERMISSION_BYPASS_EVENTS}


def get_event_additional_model():
    """
    Set a dict of additional model names.
    """
    additional_model = {}

    # list event's additional data's model
    for data_settings in DATA_SETS.event_additional_data:
        for record in data_settings.objects.all():
            key = record.serializable_value("key")
            additional_model[key] = data_settings.model_name

    return additional_model


class EventHandler(object):
    """
    """
    _additional_model = get_event_additional_model()

    def __init__(self, owner):
        """
        Initialize the handler.
        """
        self.owner = owner
        self.events = {}

        # Load events.
        event_records = DATA_SETS.event_data.objects.filter(trigger_obj=owner.get_data_key())

        for record in event_records:
            event = {}

            # Set data.
            event_type = record.type
            trigger_type = record.trigger_type

            for field in record._meta.fields:
                event[field.name] = record.serializable_value(field.name)
            event["type"] = event_type

            # Set additional data.
            if record.key in self._additional_model:
                model_name = self._additional_model[record.key]
                model_additional = apps.get_model(settings.WORLD_DATA_APP, model_name)

                try:
                    add_record = model_additional.objects.get(key = record.key)
                    # Set data.
                    for add_field in add_record._meta.fields:
                        event[add_field.name] = add_record.serializable_value(add_field.name)
                except Exception, e:
                    pass

            if not trigger_type in self.events:
                self.events[trigger_type] = []
            self.events[trigger_type].append(event)

    def can_bypass(self, character):
        """
        If the character can bypass the event.
        """
        if not character:
            return False

        if character.player:
            if character.player.is_superuser:
                # superusers can bypass events
                return True
            for perm in character.player.permissions.all():
                if perm in PERMISSION_BYPASS_EVENTS:
                    # has permission to bypass events
                    return True


    #########################
    #
    # Event triggers
    #
    #########################

    def get_function(self, event_type):
        """
        Get the function of the event type.
        """
        if event_type == defines.EVENT_ATTACK:
            return self.do_attack
        elif event_type == defines.EVENT_DIALOGUE:
            return self.do_dialogue


    def at_character_move_in(self, character):
        """
        Called when a character moves in the event handler's owner, usually a room.
        """
        if not character:
            return

        if self.can_bypass(character):
            return

        if defines.EVENT_TRIGGER_ARRIVE in self.events:
            for event in self.events[defines.EVENT_TRIGGER_ARRIVE]:
                # If has arrive event.
                if STATEMENT_HANDLER.match_condition(event["condition"], character, self.owner):
                    # If matches the condition.
                    function = self.get_function(event["type"])
                    if function:
                        function(event, character)


    def at_character_move_out(self, character):
        """
        Called when a character moves out of a room.
        """
        pass


    def at_character_die(self):
        """
        Called when a character is killed.
        """
        owner = self.owner

        if not owner:
            return

        if self.can_bypass(owner):
            return

        if defines.EVENT_TRIGGER_DIE in self.events:
            for event in self.events[defines.EVENT_TRIGGER_DIE]:
                #If has die event.
                if STATEMENT_HANDLER.match_condition(event["condition"], owner, None):
                    # If matches the condition, run event on the owner.
                    function = self.get_function(event["type"])
                    if function:
                        function(event, self)


    def at_character_kill(self, killers):
        """
        Called when a character kills others.
        This event is set on the character who is killed, and take effect on the killer!
        """
        if defines.EVENT_TRIGGER_KILL in self.events:
            for event in self.events[defines.EVENT_TRIGGER_KILL]:
                # If has kill event.
                for killer in killers:
                    if self.can_bypass(killer):
                        continue

                    if STATEMENT_HANDLER.match_condition(event["condition"], killer, self.owner):
                        function = self.get_function(event["type"])
                        if function:
                            function(event, killer)


    def at_character_traverse(self, character):
        """
        Called before a character traverses an exit.
        If returns true, the character can pass the exit, else the character can not pass the exit.
        """
        if not character:
            return True

        if self.can_bypass(character):
            return True

        triggered = False
        if defines.EVENT_TRIGGER_TRAVERSE in self.events:
            for event in self.events[defines.EVENT_TRIGGER_TRAVERSE]:
                # If has traverse event.
                if STATEMENT_HANDLER.match_condition(event["condition"], character, self.owner):
                    # If matches the condition.
                    triggered = True
                    function = self.get_function(event["type"])
                    if function:
                        function(event, character)

        return not triggered

    def do_attack(self, event, character):
        """
        Start a combat.
        """
        rand = random.random()

        # If matches the odds, put the character in combat.
        # There can be several mods with different odds.
        if rand <= event["odds"]:
            # Attack mob.
            character.attack_clone_target(event["mob"], event["level"], event["desc"])

    def do_dialogue(self, event, character):
        """
        Start a dialogue.
        """
        # Get sentence.
        npc = None
        if event["npc"]:
            npc = utils.search_obj_data_key(event["npc"])
            if npc:
                npc = npc[0]

        character.show_dialogue(npc, event["dialogue"], 0)
