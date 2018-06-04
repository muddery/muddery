"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus


class Completed(BaseQuestStatus):
    """
    The quest is completed.
    """
    key = "COMPLETED"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_completed(quest)
    
