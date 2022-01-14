"""
Event action.
"""

import random
from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.database.worlddata.worlddata import WorldData


class ActionDialogue(BaseEventAction):
    """
    Begin a dialogue.
    """
    key = "ACTION_DIALOGUE"
    name = "Dialogue"
    model_name = "action_dialogue"
    repeatedly = False

    async def func(self, event_key, character, obj):
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
                await character.show_dialogue(record.dialogue)
                return

            rand -= record.odds
