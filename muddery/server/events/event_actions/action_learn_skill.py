"""
Event action.
"""

import traceback
from muddery.server.utils.logger import logger
from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.utils.utils import async_wait


class ActionLearnSkill(BaseEventAction):
    """
    Learn a skill.
    """
    key = "ACTION_LEARN_SKILL"
    name = "Learn a Skill"
    model_name = "action_learn_skill"
    repeatedly = False

    async def func(self, event_key, character, obj):
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
        if records:
            await async_wait([character.learn_skill(r.skill, r.level, False) for r in records])
