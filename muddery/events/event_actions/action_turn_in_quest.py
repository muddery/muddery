"""
Event action.
"""

from __future__ import print_function

import random
from django.apps import apps
from django.conf import settings
from muddery.utils import utils
from muddery.events.base_event_action import BaseEventAction
from muddery.utils.localized_strings_handler import _


class ActionTurnInQuest(BaseEventAction):
    """
    Turn in a quest.
    """
    key = "ACTION_TURN_IN_QUEST"
    name = _("Turn in a Quest")
    model_name = "action_turn_in_quest"

    def func(self, event_key, character):
        """
        Turn in a quest.

        Args:
            event_key: (string) event's key.
            character: (obj) relative character.
        """
        # get action data
        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        records = model_obj.objects.filter(event_key=event_key)

        # Turn in quests.
        for record in records:
            quest_key = record.quest
            character.quest_handler.turn_in(quest_key)

    def get_quests(self, event_key):
        """
        Get relative quests of this action.

        Args:
            event_key: (string) event's key.
        """
        # get action data
        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        records = model_obj.objects.filter(event_key=event_key)
        return [record.quest for record in records]
