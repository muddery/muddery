"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus
from muddery.utils.localized_strings_handler import _


class InProgress(BaseQuestStatus):
    """
    The quest is in progress.
    """
    key = "IN_PROGRESS"
    name = _("Quest In Progress", category="quest_status")

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_in_progress(quest_key)
    
