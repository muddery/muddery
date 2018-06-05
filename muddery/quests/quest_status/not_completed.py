"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus


class NotCompleted(BaseQuestStatus):
    """
    The quest is not completed.
    """
    key = "NOT_COMPLETED"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return not caller.quest_handler.is_completed(quest_key)
    
