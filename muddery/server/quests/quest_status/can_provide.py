"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus


class CanProvide(BaseQuestStatus):
    """
    Can provide the quest.
    """
    key = "CAN_PROVIDE"
    name = "Can Provide Quest"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return caller.quest_handler.can_provide(quest_key)
