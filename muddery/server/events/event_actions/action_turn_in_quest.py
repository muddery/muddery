"""
Event action.
"""

from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.common.utils.utils import async_wait


class ActionTurnInQuest(BaseEventAction):
    """
    Turn in a quest.
    """
    key = "ACTION_TURN_IN_QUEST"
    name = "Turn in a Quest"
    model_name = "action_turn_in_quest"
    repeatedly = False

    async def func(self, event_key, character, obj):
        """
        Turn in a quest.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)

        # Turn in quests.
        if records:
            await async_wait([character.quest_handler.turn_in(r.quest) for r in records])

    def get_quests(self, event_key):
        """
        Get relative quests of this action.

        Args:
            event_key: (string) event's key.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)
        return [record.quest for record in records]
