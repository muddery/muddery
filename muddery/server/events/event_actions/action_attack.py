"""
Event action.
"""

import random
from muddery.server.utils.logger import logger
from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.database.worlddata.worlddata import WorldData


class ActionAttack(BaseEventAction):
    """
    Attack a target.
    """
    key = "ACTION_ATTACK"
    name = "Attack"
    model_name = "action_attack"
    repeatedly = False

    async def func(self, event_key, character, obj):
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
                target_key = record.mob

                base_model = ELEMENT("CHARACTER").get_base_model()
                table_data = WorldData.get_table_data(base_model, key=target_key)
                if not table_data:
                    logger.log_err("Can not create the target %s." % target_key)
                    raise MudderyError(ERR.invalid_input, _("You can not attack."))

                combat = await character.attack_temp_target(record.mob, record.level, record.desc)
                return {
                    "combat_info": combat.get_appearance(),
                    "combat_commands": character.get_combat_commands(),
                    "combat_states": await combat.get_combat_states(),
                    "from": table_data[0].name,
                    "target": character.get_name(),
                }

            rand -= record.odds
