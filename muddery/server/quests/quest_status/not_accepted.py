"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus
from muddery.server.utils.localized_strings_handler import _


class NotAccepted(BaseQuestStatus):
    """
    The quest has not been accepted.
    """
    key = "NOT_ACCEPTED"
    name = _("Quest Not Accepted", category="quest_status")

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return not caller.quest_handler.is_finished(quest_key) and \
            not caller.quest_handler.is_in_progress(quest_key)

