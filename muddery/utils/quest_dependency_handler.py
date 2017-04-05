"""
QuestDependencyHandler deals quest's dependencies.
"""

from muddery.utils import defines
from muddery.worlddata.data_sets import DATA_SETS
from evennia.utils import logger


class QuestDependencyHandler(object):
    """
    This class handels the relation of quest.
    """
    def __init__(self):
        """
        Initialize handler
        """
        self.quest_depencences = {}


    def get_quest_dependencies(self, quest):
        """
        Get quest's dependencies.
        """
        if not quest:
            return

        self.load_dependencies_cache(quest)
        return self.quest_depencences[quest]


    def load_dependencies_cache(self, quest):
        """
        To reduce database accesses, add a cache.
        """
        if not quest:
            return

        if quest in self.quest_depencences:
            # already cached
            return

        # Add cache of the whole dialogue.
        self.quest_depencences[quest] = []
        
        # Get db model
        dependencies = DATA_SETS.quest_dependencies.objects.filter(quest=quest)

        # Add db fields to data object.
        data = []
        for dependency in dependencies:
            data.append({"quest": dependency.dependency,
                         "type": dependency.type})

        # Add to cache.
        self.quest_depencences[quest] = data


    def match_quest_dependencies(self, caller, quest):
        """
        If the quest matches its dependencies.
        """
        if not caller:
            return False

        if not quest:
            return False

        for dependency in self.get_quest_dependencies(quest):
            # match each dependency
            if not self.match_dependency(caller, dependency["quest"], dependency["type"]):
                return False

        return True


    def match_dependency(self, caller, quest, dependency_type):
        """
        check a dependency
        """
        if dependency_type == defines.DEPENDENCY_QUEST_CAN_PROVIDE:
            if not caller.quest_handler.can_provide(quest):
                return False
        elif dependency_type == defines.DEPENDENCY_QUEST_IN_PROGRESS:
            if not caller.quest_handler.is_in_progress(quest):
                return False
        elif dependency_type == defines.DEPENDENCY_QUEST_NOT_IN_PROGRESS:
            if caller.quest_handler.is_in_progress(quest):
                return False
        elif dependency_type == defines.DEPENDENCY_QUEST_ACCOMPLISHED:
            if not caller.quest_handler.is_accomplished(quest):
                return False
        elif dependency_type == defines.DEPENDENCY_QUEST_NOT_ACCOMPLISHED:
            if not caller.quest_handler.is_in_progress(quest):
                return False
            if caller.quest_handler.is_accomplished(quest):
                return False
        elif dependency_type == defines.DEPENDENCY_QUEST_COMPLETED:
            if not caller.quest_handler.is_completed(quest):
                return False
        elif dependency_type == defines.DEPENDENCY_QUEST_NOT_COMPLETED:
            if caller.quest_handler.is_completed(quest):
                return False
        elif dependency_type == defines.DEPENDENCY_QUEST_ACCEPTED:
            if not caller.quest_handler.is_completed(quest) and \
               not caller.quest_handler.is_in_progress(quest):
                return False
        elif dependency_type == defines.DEPENDENCY_QUEST_NOT_ACCEPTED:
            if caller.quest_handler.is_completed(quest) or \
               caller.quest_handler.is_in_progress(quest):
                return False

        return True


    def clear(self):
        """
        clear cache
        """
        self.quest_depencences = {}


# main quest_dependendy_handler
QUEST_DEP_HANDLER = QuestDependencyHandler()
