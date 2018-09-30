"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus


class Finished(BaseQuestStatus):
    """
    The quest is finished.
    """
    key = "FINISHED"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_finished(quest_key)
    
