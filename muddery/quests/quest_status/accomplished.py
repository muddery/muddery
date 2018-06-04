"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus


class Accomplished(BaseQuestStatus):
    """
    The quest is accomplished.
    """
    key = "ACCOMPLISHED"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_accomplished(quest_key)
    
