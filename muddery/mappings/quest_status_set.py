"""
All available event actions.
"""

from __future__ import print_function

from django.conf import settings
from muddery.utils.utils import classes_in_path
from muddery.quests.base_quest_status import BaseQuestStatus
from evennia.utils import logger


class QuestStatusSet(object):
    """
    All available quest status.
    """
    def __init__(self):
        self.dict = {}
        self.load()

    def load(self):
        """
        Add all quest status from the path.
        """
        # load classes
        for cls in classes_in_path(settings.PATH_QUEST_STATUS_BASE, BaseQuestStatus):
            key = cls.key

            if self.dict.has_key(key):
                logger.log_infomsg("Quest status %s is replaced by %s." % (key, cls))

            self.dict[key] = cls()

    def get(self, key):
        """
        Get the function of the event action.
        """
        return self.dict[key]

    def all(self):
        """
        Add all forms from the form path.
        """
        return self.dict.keys()


QUEST_STATUS_SET = QuestStatusSet()
