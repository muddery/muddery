"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus
from muddery.server.utils.localized_strings_handler import _


class Accepted(BaseQuestStatus):
    """
    The quest has been accepted.
    """
    key = "ACCEPTED"
    name = _("Quest Accepted", category="quest_status")

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_finished(quest_key) or \
            caller.quest_handler.is_in_progress(quest_key)
