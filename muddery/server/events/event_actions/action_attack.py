"""
Event action.
"""

import random
from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.dao.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _


class ActionAttack(BaseEventAction):
    """
    Attack a target.
    """
    key = "ACTION_ATTACK"
    name = _("Attack", category="event_actions")
    model_name = "action_attack"
    repeatedly = False

    def func(self, event_key, character, obj):
        """
        Start a combat.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)

        rand = random.random()

        # If matches the odds, put the character in combat.
        # There can be several mods with different odds.
        for record in records:
            if rand <= record.odds:
                # Attack mob.
                character.attack_temp_target(record.mob, record.level, record.desc)
                return

            rand -= record.odds
