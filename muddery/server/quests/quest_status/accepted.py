"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus


class Accepted(BaseQuestStatus):
    """
    The quest has been accepted.
    """
    key = "ACCEPTED"
    name = "Quest Accepted"

    async def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return await caller.quest_handler.is_finished(quest_key) or \
            await caller.quest_handler.is_in_progress(quest_key)
