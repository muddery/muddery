"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus
from muddery.utils.localized_strings_handler import _


class CanNotProvide(BaseQuestStatus):
    """
    Can not provide the quest.
    """
    key = "CAN_NOT_PROVIDE"
    name = _("Can Not Provide Quest", category="quest_status")

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return not caller.quest_handler.can_provide(quest_key)
