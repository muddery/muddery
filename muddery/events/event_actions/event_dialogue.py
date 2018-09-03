"""
Event action.
"""

import random
from django.apps import apps
from django.conf import settings
from muddery.utils import utils
from muddery.events.base_event_action import BaseEventAction


class EventDialogue(BaseEventAction):
    """
    Event to start a combat.
    """
    key = "EVENT_DIALOGUE"
    model_name = "event_dialogues"

    def func(self, event_key, character):
        """
        Start a dialogue.

        Args:
            event_key: (string) event's key.
            character: (obj) relative character.
        """
        # get action data
        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        records = model_obj.objects.filter(event_key=event_key)

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

                character.show_dialogue(npc, record.dialogue, 0)
                return

            rand -= record.odds
