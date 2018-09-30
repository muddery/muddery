"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus


class NotFinished(BaseQuestStatus):
    """
    The quest is not finished.
    """
    key = "NOT_FINISHED"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return not caller.quest_handler.is_finished(quest_key)
    
