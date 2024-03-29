"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus


class Finished(BaseQuestStatus):
    """
    The quest is finished.
    """
    key = "FINISHED"
    name = "Quest Finished"

    async def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.is_finished(quest_key)
