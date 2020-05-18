"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus
from muddery.server.utils.localized_strings_handler import _


class Accomplished(BaseQuestStatus):
    """
    The quest's objectives are accomplished.
    """
    key = "ACCOMPLISHED"
    name = _("Objectives Accomplished", category="quest_status")

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_accomplished(quest_key)
