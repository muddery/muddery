"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus


class NotFinished(BaseQuestStatus):
    """
    The quest is not finished.
    """
    key = "NOT_FINISHED"
    name = "Quest Not Finished"

    async def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return not await caller.quest_handler.is_finished(quest_key)
