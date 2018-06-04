"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus


class NotAccomplished(BaseQuestStatus):
    """
    The quest has not accomplished.
    """
    key = "NOT_ACCOMPLISHED"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_in_progress(quest) and \
            not caller.quest_handler.is_accomplished(quest)
    
