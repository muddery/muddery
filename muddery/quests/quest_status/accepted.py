"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus


class Accpeted(BaseQuestStatus):
    """
    The call has accepted the quest.
    """
    key = "ACCEPTED"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_completed(quest) or \
            caller.quest_handler.is_in_progress(quest)
    
