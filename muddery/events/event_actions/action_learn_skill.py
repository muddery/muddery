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


class ActionLearnSkill(BaseEventAction):
    """
    Learn a skill.
    """
    key = "ACTION_LEARN_SKILL"
    name = _("Learn a Skill")
    model_name = "action_learn_skill"

    def func(self, event_key, character):
        """
        Learn a skill.

        Args:
            event_key: (string) event's key.
            character: (obj) relative character.
        """
        # get action data
        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        records = model_obj.objects.filter(event_key=event_key)

        # Learn skills.
        for record in records:
            skill_key = record.skill
            character.learn_skill(skill_key, False, False)
