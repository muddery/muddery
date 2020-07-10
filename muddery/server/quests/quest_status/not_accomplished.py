"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus
from muddery.server.utils.localized_strings_handler import _


class NotAccomplished(BaseQuestStatus):
    """
    The quest's objectives are not accomplished.
    """
    key = "NOT_ACCOMPLISHED"
    name = _("Objectives Not Accomplished", category="quest_status")

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_in_progress(quest_key) and \
            not caller.quest_handler.is_accomplished(quest_key)

