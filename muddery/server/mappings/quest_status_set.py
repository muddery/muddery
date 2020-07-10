"""
All available event actions.
"""

from django.conf import settings
from evennia.utils import logger
from muddery.server.utils.utils import classes_in_path
from muddery.server.quests.base_quest_status import BaseQuestStatus


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

            if key in self.dict:
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

    def choice_all(self):
        """
        Get all event types and names for form choice.
        """
        return [(key, "%s (%s)" % (value.name, key)) for key, value in self.dict.items()]


QUEST_STATUS_SET = QuestStatusSet()
