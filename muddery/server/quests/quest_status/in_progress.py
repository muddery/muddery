"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus


class InProgress(BaseQuestStatus):
    """
    The quest is in progress.
    """
    key = "IN_PROGRESS"
    name = "Quest In Progress"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_in_progress(quest_key)
    
