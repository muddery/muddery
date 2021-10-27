"""
Event action.
"""

import traceback
from muddery.server.utils import logger
from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.database.worlddata.worlddata import WorldData
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
            try:
                character.learn_skill(record.skill, record.level, False)
            except Exception as e:
                traceback.print_exc()
                logger.log_err("Can not learn skill %s %s" % (type(e).__name__, e))
                pass
