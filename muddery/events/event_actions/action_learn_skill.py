"""
Event action.
"""

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
    name = _("Learn a Skill", category="event_actions")
    model_name = "action_learn_skill"
    repeatedly = False

    def func(self, event_key, character, obj):
        """
        Learn a skill.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        # get action data
        model_obj = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        records = model_obj.objects.filter(event_key=event_key)

        # Learn skills.
        for record in records:
            skill_key = record.skill
            character.learn_skill(skill_key, False, False)
