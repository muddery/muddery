"""
Event action.
"""

from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.dao.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _


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
        records = WorldData.get_table_data(self.model_name, event_key=event_key)

        # Learn skills.
        for record in records:
            skill_key = record.skill
            character.learn_skill(skill_key, False, False)
