"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus
from muddery.server.utils.localized_strings_handler import _


class Finished(BaseQuestStatus):
    """
    The quest is finished.
    """
    key = "FINISHED"
    name = _("Quest Finished", category="quest_status")

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_finished(quest_key)
    
