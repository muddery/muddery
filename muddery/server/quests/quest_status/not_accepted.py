"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus


class NotAccepted(BaseQuestStatus):
    """
    The quest has not been accepted.
    """
    key = "NOT_ACCEPTED"
    name = "Quest Not Accepted"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return not caller.quest_handler.is_finished(quest_key) and \
            not caller.quest_handler.is_in_progress(quest_key)

