"""
EventHandler handles all events. The handler sets on every object.
"""

import re
import random
from muddery.utils import defines
from muddery.utils.builder import build_object
from muddery.utils.script_handler import SCRIPT_HANDLER
from muddery.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.utils import utils
from django.conf import settings
from django.apps import apps
from evennia.utils import logger
from evennia import create_script

PERMISSION_BYPASS_EVENTS = {perm.lower() for perm in settings.PERMISSION_BYPASS_EVENTS}

def get_event_additional_model():
    """
    Set a dict of additional model names.
    """
    additional_model = {}

    # list event's additional data's model
    for model_name in settings.EVENT_ADDITIONAL_DATA:
        model_data = apps.get_model(settings.WORLD_DATA_APP, model_name)
        if model_data:
            # Get records.
            for record in model_data.objects.all():
                key = record.serializable_value("key")
                additional_model[key] = model_name

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
        event_records = []
        model_events = apps.get_model(settings.WORLD_DATA_APP, settings.EVENT_DATA)
        if model_events:
            # Get records.
            event_records = model_events.objects.filter(trigger_obj=owner.get_data_key())

            for record in event_records:
                event = {}

                # Set data.
                event_type = record.type.type_id
                trigger_type = record.trigger_type.type_id

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

                """
                if event_record.type == defines.EVENT_ATTACK:
                    self.create_event_attack(event)
                elif event_record.type == defines.EVENT_DIALOGUE:
                    self.create_event_dialogue(event)
                """

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
                if SCRIPT_HANDLER.match_condition(character, self.owner, event["condition"]):
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
                if SCRIPT_HANDLER.match_condition(owner, None, event["condition"]):
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

                    if SCRIPT_HANDLER.match_condition(killer, self.owner, event["condition"]):
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
                if SCRIPT_HANDLER.match_condition(character, self.owner, event["condition"]):
                    # If matches the condition.
                    triggered = True
                    function = self.get_function(event["type"])
                    if function:
                        function(event, character)

        return not triggered


    #########################
    #
    # Event attack
    #
    #########################

    def create_event_attack(self, event):
        """
        Create a combat event, load combat infos.
        """
        event["type"] = defines.EVENT_ATTACK
        event["function"] = self.do_attack

        mob_records = []
        model_mobs = apps.get_model(settings.WORLD_DATA_APP, settings.EVENT_MOBS)
        if model_mobs:
            # Get records.
            mob_records = model_mobs.objects.filter(key=event["key"])

        data = []
        for mob_record in mob_records:
            mob = {"mob": mob_record.mob,
                   "level": mob_record.level,
                   "odds": mob_record.odds,
                   "desc": mob_record.desc}
            data.append(mob)
        event["data"] = data

        return event


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


    def create_event_dialogue(self, event):
        """
        Create a dialogue event, load dialog info.
        """
        event["type"] = defines.EVENT_DIALOGUE
        event["function"] = self.do_dialogue

        try:
            model_dialogues = apps.get_model(settings.WORLD_DATA_APP, settings.EVENT_DIALOGUES)
            if model_dialogues:
                # Get record.
                dialogue_record = model_dialogues.objects.get(key=event["key"])
                data = {"dialogue": dialogue_record.dialogue,
                        "npc": dialogue_record.npc}
                event["data"] = data
        except Exception, e:
            logger.log_errmsg("Can't load event dialogue %s: %s" % (event["key"], e))

        return event


    def do_dialogue(self, event, character):
        """
        Start a dialogue.
        """
        # Get sentence.
        sentence = DIALOGUE_HANDLER.get_sentence(event["dialogue"], 0)

        if sentence:
            npc = None
            if event["npc"]:
                npc = utils.search_obj_data_key(event["npc"])
                if npc:
                    npc = npc[0]

            speaker = DIALOGUE_HANDLER.get_dialogue_speaker(character, npc, sentence["speaker"])
            dlg = {"speaker": speaker,
                   "dialogue": sentence["dialogue"],
                   "sentence": sentence["sentence"],
                   "content": sentence["content"]}

            if npc:
                dlg["npc"] = npc.dbref

            character.msg({"dialogue": [dlg]})
