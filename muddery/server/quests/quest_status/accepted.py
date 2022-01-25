"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus
from muddery.server.utils.utils import async_gather


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

        results = [
            caller.quest_handler.is_finished(quest_key),
            caller.quest_handler.is_in_progress(quest_key),
        ]

        return results[0] or results[1]
