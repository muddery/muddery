"""
All available event actions.
"""

from __future__ import print_function

from muddery.utils import defines


class QuestDependencySet(object):
    """
    All available quest dependencies.
    """
    def __init__(self):
        self.dict = {}
        self.types = [
            defines.DEPENDENCY_QUEST_CAN_PROVIDE,
            defines.DEPENDENCY_QUEST_ACCEPTED,
            defines.DEPENDENCY_QUEST_NOT_ACCEPTED,
            defines.DEPENDENCY_QUEST_IN_PROGRESS,
            defines.DEPENDENCY_QUEST_NOT_IN_PROGRESS,
            defines.DEPENDENCY_QUEST_ACCOMPLISHED,          # quest accomplished
            defines.DEPENDENCY_QUEST_NOT_ACCOMPLISHED,      # quest accepted but not accomplished
            defines.DEPENDENCY_QUEST_COMPLETED,             # quest complete
            defines.DEPENDENCY_QUEST_NOT_COMPLETED,         # quest accepted but not complete
        ]

    def all(self):
        """
        Add all forms from the form path.
        """
        return self.types


QUEST_DEPENDENCY_SET = QuestDependencySet()

