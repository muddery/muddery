"""
EventHandler handles all events. The handler sets on every object.
"""

import re
import random
from muddery.utils import defines
from muddery.utils.builder import build_object
from muddery.utils import script_handler
from muddery.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.utils import utils
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger
from evennia import create_script

PERMISSION_BYPASS_EVENTS = {perm.lower() for perm in settings.PERMISSION_BYPASS_EVENTS}

class EventHandler(object):
    """
    """
    def __init__(self, owner):
        """
        Initialize the handler.
        """
        self.owner = owner
        self.events = {}

        # Load events.
        event_records = []
        model_events = get_model(settings.WORLD_DATA_APP, settings.EVENT_DATA)
        if model_events:
            # Get records.
            event_records = model_events.objects.filter(object=owner.get_info_key())

        for event_record in event_records:
            if not event_record.trigger in self.events:
                self.events[event_record.trigger] = []

            event = {"key": event_record.key,
                     "object": event_record.object,
                     "condition": event_record.condition}

            if event_record.type == defines.EVENT_ATTACK:
                self.create_event_attack(event)
            elif event_record.type == defines.EVENT_DIALOGUE:
                self.create_event_dialogue(event)

            self.events[event_record.trigger].append(event)


    def at_character_move_in(self, character):
        """
        Called when a character moves in the event handler's owner, usually a room.
        """
        if not character:
            return

        if character.player:
            if character.player.is_superuser:
                # superusers can bypass events
                return
            for perm in character.player.permissions.all():
                if perm in PERMISSION_BYPASS_EVENTS:
                    # has permission to bypass events
                    return

        if defines.EVENT_TRIGGER_ARRIVE in self.events:
            for event in self.events[defines.EVENT_TRIGGER_ARRIVE]:
                # If has arrive event.
                if script_handler.match_condition(character, event["condition"]):
                    # If matches the condition.
                    event["function"](event["data"], character)


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

        if owner.player:
            if owner.player.is_superuser:
                # superusers can bypass events
                return
            for perm in owner.player.permissions.all():
                if perm in PERMISSION_BYPASS_EVENTS:
                    # has permission to bypass events
                    return

        if defines.EVENT_TRIGGER_DIE in self.events:
            for event in self.events[defines.EVENT_TRIGGER_DIE]:
                #If has die event.
                if script_handler.match_condition(owner, event["condition"]):
                    # If matches the condition, run event on the owner.
                    event["function"](event["data"], owner)


    def at_character_kill(self, killers):
        """
        Called when a character kills others.
        This event is set on the character who is killed, and take effect on the killer!
        """
        if defines.EVENT_TRIGGER_KILL in self.events:
            for event in self.events[defines.EVENT_TRIGGER_KILL]:
                # If has kill event.
                for killer in killers:
                    if killer.player:
                        if killer.player.is_superuser:
                            # superusers can bypass events
                            continue
                        for perm in killer.player.permissions.all():
                            if perm in PERMISSION_BYPASS_EVENTS:
                                # has permission to bypass events
                                continue


                    if script_handler.match_condition(killer, event["condition"]):
                        event["function"](event["data"], killer)


    def create_event_attack(self, event):
        """
        Create a combat event, load combat infos.
        """
        event["type"] = defines.EVENT_ATTACK
        event["function"] = self.do_attack

        mob_records = []
        model_mobs = get_model(settings.WORLD_DATA_APP, settings.EVENT_MOBS)
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


    def do_attack(self, data, character):
        """
        Start a combat.
        """
        rand = random.random()
        for item in data:
            # If matches the odds, put the character in combat.
            # There can be several mods with different odds.
            if rand >= item["odds"]:
                rand -= item["odds"]
                continue

            # Create mob.
            mob = build_object(item["mob"])
            if not mob:
                return

            mob.set_level(item["level"])

            # create a new combat handler
            chandler = create_script("combat_handler.CombatHandler")
            
            # set teams and desc
            chandler.set_combat({1: [mob], 2: [character]}, item["desc"])


    def create_event_dialogue(self, event):
        """
        Create a dialogue event, load dialog info.
        """
        event["type"] = defines.EVENT_DIALOGUE
        event["function"] = self.do_dialogue

        try:
            model_dialogues = get_model(settings.WORLD_DATA_APP, settings.EVENT_DIALOGUES)
            if model_dialogues:
                # Get record.
                dialogue_record = model_dialogues.objects.get(key=event["key"])
                data = {"dialogue": dialogue_record.dialogue,
                        "npc": dialogue_record.npc}
                event["data"] = data
        except Exception, e:
            print "Can't load event dialogue %s: %s" % (event["key"], e)

        return event


    def do_dialogue(self, data, character):
        """
        Start a dialogue.
        """
        # Get sentence.
        sentence = DIALOGUE_HANDLER.get_sentence(data["dialogue"], 0)

        if sentence:
            npc = None
            if data["npc"]:
                npc = utils.search_obj_info_key(data["npc"])
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
