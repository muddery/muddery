"""
QuestHandler
"""

import re
from muddery.utils import defines
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import logger


class QuestHandler(object):
    """
    """
    def __init__(self):
        """
        Initialize handler
        """
        self.quest_depencences = {}


    def has_quest(self, quest):
        """
        Checks if has the given quest.
        """
        return quest in self.obj.quests


    def quest_finished(self, quest):
        """
        Checks if the given quest is finished.
        """
        return quest in self.obj.quests_finished()


    def at_character_move_in(self, location):
        """
        """
        pass


    def at_character_move_out(self):
        """
        """
        pass


    def match_condition(self, caller, condition):
        """
        check condition
        """
        if not condition:
            return True

        # add "caller" to condition
        condition = self.safe_statement(condition)

        try:
            # check it
            match = eval(condition, {"caller": caller})
        except Exception, e:
            logger.log_errmsg("match_condition error:%s %s" % (condition, e))
            return False

        return match


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
        check dependences
        """
        if not caller:
            return False

        if not quest:
            return False

        self.load_dependences_cache(quest)

        for dependence in self.quest_depencences[quest]:
            if dependence["type"] == defines.DEPENDENCE_QUEST_IN_PROGRESS:
                if not caller.is_quest_in_progress(dependence["quest"]):
                    return False
            elif dependence["type"] == defines.DEPENDENCE_QUEST_NOT_IN_PROGRESS:
                if caller.is_quest_in_progress(dependence["quest"]):
                    return False
            elif dependence["type"] == defines.DEPENDENCE_QUEST_FINISHED:
                if not caller.is_quest_finished(dependence["quest"]):
                    return False
            elif dependence["type"] == defines.DEPENDENCE_QUEST_UNFINISHED:
                if caller.is_quest_finished(dependence["quest"]):
                    return False

        return True


    def do_quest_action(self, caller, quest):
        """
        do quest's action
        """
        # do dialogue's action
        self.do_action(caller, quest["action"])


    def do_action(self, caller, action):
        """
        do action
        """
        if not action:
            return

        # add "caller" to action
        action = self.safe_statement(action)

        # run action
        try:
            eval(action, {"caller": caller})
        except Exception, e:
            logger.log_errmsg("do_dialogue_action error:%s %s" % (action, e))
            
        return


    def clear(self):
        """
        clear cache
        """
        self.dialogue_storage = {}


    re_words = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)|(\"(.*?)\")")
    def safe_statement(self, statement):
        """
        Add "caller." before every words.
        """
        return self.re_words.sub(self.sub_statement, statement)


    statement_keywords = {"not", "and", "or"}
    def sub_statement(self, match):
        """
        Replace <match> with caller.<match> except key words.
        """
        match = match.group()

        # keep the key words
        if match in self.statement_keywords:
            return match

        # keep the strings in quotes
        if match[0] == "\"" and match[-1] == "\"":
            return match

        return "caller." + match


# main questhandler
QUEST_HANDLER = QuestHandler()
