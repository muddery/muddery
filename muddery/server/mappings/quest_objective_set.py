"""
All available event actions.
"""

from muddery.common.utils import defines
from muddery.server.utils.localized_strings_handler import _


class QuestObjectiveSet(object):
    """
    All available quest objectives.
    """
    def __init__(self):
        # finish a dialogue, object: dialogue_id
        self.dict = {
            defines.OBJECTIVE_TALK: {
                "name": "Talk",
            },
            # arrive a room, object: room_id
            defines.OBJECTIVE_ARRIVE: {
                "name": "Arrive"
            },
            # get some objects, object: object_id
            defines.OBJECTIVE_OBJECT: {
                "name": "Get"
            },
            # kill some characters, object: character_id
            defines.OBJECTIVE_KILL: {
                "name": "Kill"
            },
        }

    def all(self):
        """
        Add all forms from the form path.
        """
        return self.dict.keys()


QUEST_OBJECTIVE_SET = QuestObjectiveSet()

