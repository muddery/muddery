"""
Event action.
"""

from muddery.server.events.base_event_action import BaseEventAction
from muddery.server.database.dao.worlddata import WorldData
from muddery.server.utils.localized_strings_handler import _


class ActionTurnInQuest(BaseEventAction):
    """
    Turn in a quest.
    """
    key = "ACTION_TURN_IN_QUEST"
    name = _("Turn in a Quest", category="event_actions")
    model_name = "action_turn_in_quest"
    repeatedly = False

    def func(self, event_key, character, obj):
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
        for record in records:
            quest_key = record.quest
            character.quest_handler.turn_in(quest_key)

    def get_quests(self, event_key):
        """
        Get relative quests of this action.

        Args:
            event_key: (string) event's key.
        """
        # get action data
        records = WorldData.get_table_data(self.model_name, event_key=event_key)
        return [record.quest for record in records]
