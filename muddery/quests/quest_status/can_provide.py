"""
Quest status.
"""

from muddery.quests.base_quest_status import BaseQuestStatus


class CanProvide(BaseQuestStatus):
    """
    The call can provide the quest.
    """
    key = "CAN_PROVIDE"

    def match(self, caller, quest_key):
        """
        Check.
        """
        print("can_provide_quest: %s" % quest_key)
        if not caller:
            return False

        return caller.quest_handler.can_provide(quest_key)
    
