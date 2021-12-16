"""
Quest status.
"""

from muddery.server.quests.base_quest_status import BaseQuestStatus


class CanNotProvide(BaseQuestStatus):
    """
    Can not provide the quest.
    """
    key = "CAN_NOT_PROVIDE"
    name = "Can Not Provide Quest"

    def match(self, caller, quest_key):
        """
        Check.
        """
        if not caller:
            return False

        return not caller.quest_handler.can_provide(quest_key)
