"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus


class NotAccomplished(BaseQuestStatus):
    """
    The quest's objectives are not accomplished.
    """
    key = "NOT_ACCOMPLISHED"
    name = "Objectives Not Accomplished"

    async def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        results = []
        results.append(caller.quest_handler.is_in_progress(quest_key))
        results.append(await caller.quest_handler.is_accomplished(quest_key))

        return results[0] and not results[1]

