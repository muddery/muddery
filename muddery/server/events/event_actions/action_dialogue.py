"""
Event action.
"""

import random
from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.database.dao.worlddata import WorldData
from muddery.server.utils import utils
from muddery.server.utils.localized_strings_handler import _


class ActionDialogue(BaseEventAction):
    """
    Begin a dialogue.
    """
    key = "ACTION_DIALOGUE"
    name = _("Dialogue", category="event_actions")
    model_name = "action_dialogue"
    repeatedly = False

    def func(self, event_key, character, obj):
        """
        Start a dialogue.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)

        # Get sentence.
        rand = random.random()

        # If matches the odds, put the character in combat.
        # There can be several mods with different odds.
        for record in records:
            if rand <= record.odds:
                # Make dialogue.
                npc = None
                if record.npc:
                    npc = utils.search_obj_data_key(record.npc)
                    if npc:
                        npc = npc[0]

                character.show_dialogue(record.dialogue, npc)
                return

            rand -= record.odds
