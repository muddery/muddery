"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus
from muddery.server.utils.localized_strings_handler import _


class NotFinished(BaseQuestStatus):
    """
    The quest is not finished.
    """
    key = "NOT_FINISHED"
    name = _("Quest Not Finished", category="quest_status")

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return not caller.quest_handler.is_finished(quest_key)
