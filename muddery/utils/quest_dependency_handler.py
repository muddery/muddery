"""
QuestDependencyHandler deals quest's dependencies.
"""

from muddery.utils import defines
from django.conf import settings
from django.db.models.loading import get_model
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


    def get_quest_dependences(self, quest):
        """
        Get quest's dependences.
        """
        if not quest:
            return

        self.load_dependences_cache(quest)
        return self.quest_depencences[quest]


    def load_dependences_cache(self, quest):
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
        dependences = []
        model_dependences = get_model(settings.WORLD_DATA_APP, settings.QUEST_DEPENDENCY)
        if model_dependences:
            # Get records.
            dependences = model_dependences.objects.filter(quest=quest)


        # Add db fields to data object.
        data = []
        for dependence in dependences:
            data.append({"quest": dependence.dependence_id,
                         "type": dependence.type})

        # Add to cache.
        self.quest_depencences[quest] = data


    def match_quest_dependences(self, caller, quest):
        """
        If the quest matches its dependences.
        """
        if not caller:
            return False

        if not quest:
            return False

        for dependence in self.get_quest_dependences(quest):
            # match each dependence
            if not self.match_dependence(caller, dependence["quest"], dependence["type"]):
                return False

        return True


    def match_dependence(self, caller, quest, dependence_type):
        """
        check a dependence
        """
        if dependence_type == defines.DEPENDENCE_QUEST_CAN_PROVIDE:
            if not this.can_provide_quest(caller, quest):
                return False
        elif dependence_type == defines.DEPENDENCE_QUEST_IN_PROGRESS:
            if not caller.quest.is_in_progress(quest):
                return False
        elif dependence_type == defines.DEPENDENCE_QUEST_NOT_IN_PROGRESS:
            if caller.quest.is_in_progress(quest):
                return False
        elif dependence_type == defines.DEPENDENCE_QUEST_FINISHED:
            if not caller.quest.is_finished(quest):
                return False
        elif dependence_type == defines.DEPENDENCE_QUEST_UNFINISHED:
            if caller.quest.is_finished(quest):
                return False
        elif dependence_type == defines.DEPENDENCE_QUEST_ACCEPTED:
            if not caller.quest.is_finished(quest) and \
               not caller.quest.is_in_progress(quest):
                return False
        elif dependence_type == defines.DEPENDENCE_QUEST_NOT_ACCEPTED:
            if caller.quest.is_finished(quest) or \
               caller.quest.is_in_progress(quest):
                return False

        return True


    def can_provide_quest(self, caller, quest):
        """
        whether can provide quest or not
        """
        if not caller:
            return False
                    
        if not quest:
            return False
                
        if caller.quest.is_finished(dependence["quest"]):
            return False
            
        return True


    def clear(self):
        """
        clear cache
        """
        self.quest_depencences = {}


# main quest_dependendy_handler
QUEST_DEP_HANDLER = QuestDependencyHandler()
