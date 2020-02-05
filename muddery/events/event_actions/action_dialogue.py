"""
Event action.
"""

import random
from django.apps import apps
from django.conf import settings
from muddery.utils import utils
from muddery.events.base_event_action import BaseEventAction
from muddery.utils.localized_strings_handler import _


class ActionDialogue(BaseEventAction):
    """
    Begin a dialogue.
    """
    key = "ACTION_DIALOGUE"
    name = _("Dialogue", category="actions")
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

                character.show_dialogue(npc, record.dialogue)
                return

            rand -= record.odds
