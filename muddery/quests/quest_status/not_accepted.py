"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus


class NotAccpeted(BaseQuestStatus):
    """
    The call has not accepted the quest.
    """
    key = "NOT_ACCEPTED"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return not caller.quest_handler.is_completed(quest_key) and \
            not caller.quest_handler.is_in_progress(quest_key)

