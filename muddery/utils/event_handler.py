"""
EventHandler
"""

import re
import random
from muddery.utils import defines
from muddery.utils.builder import build_object
from muddery.utils import script_handler
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger
from evennia import create_script


class EventHandler(object):
    """
    """
    def __init__(self, owner):
        """
        Initialize handler
        """
        self.owner = owner
        self.events = {}

        event_records = []
        model_events = get_model(settings.WORLD_DATA_APP, settings.EVENT_DATA)
        if model_events:
            # Get records.
            event_records = model_events.objects.filter(key=owner.get_info_key)

        for event_record in event_records:
            if not event_record.trigger in self.events:
                self.events[event_record.trigger] = []

            event = {"condition": event_record.condition}

            if event_record.type == defines.EVENT_ATTACK:
                self.create_event_attack(event)

            self.events[event_record.trigger].append(event)


    def at_character_move_in(self, character):
        """
        """
        if not character:
            return

        if character.player.is_superuser:
            # ban events on superusers
            return

        if defines.EVENT_TRIGGER_ARRIVE in self.events:
            for event in self.events[defines.EVENT_TRIGGER_ARRIVE]:
                if script_handler.match_condition(character, event["condition"]):
                    event["function"](event["data"], character)


    def at_character_move_out(self):
        """
        """
        pass


    def create_event_attack(self, event):
        """
        """
        event["type"] = defines.EVENT_ATTACK
        event["function"] = self.do_attack

        mob_records = []
        model_mobs = get_model(settings.WORLD_DATA_APP, settings.EVENT_MOBS)
        if model_mobs:
            # Get records.
            mob_records = model_mobs.objects.filter(key=self.owner.get_info_key)

        data = []
        for mob_record in mob_records:
            mob = {"mob": mob_record.mob,
                   "level": mob_record.level,
                   "odds": mob_record.odds}
            data.append(mob)
        event["data"] = data

        return event


    def do_attack(self, data, character):
        """
        """
        rand = random.random()
        for item in data:
            if rand >= item["odds"]:
                rand -= item["odds"]
                continue

            mob = build_object(item["mob"])
            if not mob:
                return

            mob.set_level(item["level"])

            # create a new combat handler
            chandler = create_script("combat_handler.CombatHandler")
            chandler.add_characters([mob, character])
