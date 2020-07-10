"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus
from muddery.server.utils.localized_strings_handler import _


class CanProvide(BaseQuestStatus):
    """
    Can provide the quest.
    """
    key = "CAN_PROVIDE"
    name = _("Can Provide Quest", category="quest_status")

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.can_provide(quest_key)
