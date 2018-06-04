"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus


class NotInProgress(BaseQuestStatus):
    """
    The call can provide the quest.
    """
    key = "NOT_IN_PROGRESS"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return not caller.quest_handler.can_provide(quest_key)
    
