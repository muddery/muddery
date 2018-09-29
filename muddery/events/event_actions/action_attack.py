"""
Event action.
"""

from __future__ import print_function

import random
from django.apps import apps
from django.conf import settings
from muddery.events.base_event_action import BaseEventAction
from muddery.utils.localized_strings_handler import _


class ActionAttack(BaseEventAction):
    """
    Attack a target.
    """
    key = "ACTION_ATTACK"
    name = _("Attack")
    model_name = "action_attack"

    def func(self, event_key, character):
        """
        Start a combat.

        Args:
            event_key: (string) event's key.
            character: (obj) relative character.
        """
        # get action data
        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        records = model_obj.objects.filter(event_key=event_key)

        rand = random.random()

        # If matches the odds, put the character in combat.
        # There can be several mods with different odds.
        for record in records:
            if rand <= record.odds:
                # Attack mob.
                character.attack_temp_target(record.mob, record.level, record.desc)
                return

            rand -= record.odds
    
