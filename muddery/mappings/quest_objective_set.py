"""
All available event actions.
"""

from __future__ import print_function

from muddery.utils import defines


class QuestObjectiveSet(object):
    """
    All available quest objectives.
    """
    def __init__(self):
        self.dict = {}
        self.types = [
            defines.OBJECTIVE_TALK,         # finish a dialogue, object: dialogue_id
            defines.OBJECTIVE_ARRIVE,       # arrive a room, object: room_id
            defines.OBJECTIVE_OBJECT,       # get some objects, object: object_id
            defines.OBJECTIVE_KILL,         # kill some characters, object: character_id
        ]

    def all(self):
        """
        Add all forms from the form path.
        """
        return self.types


QUEST_OBJECTIVE_SET = QuestObjectiveSet()

