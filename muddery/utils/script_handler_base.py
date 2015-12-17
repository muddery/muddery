"""
This model handle scripts.
"""

import re
import traceback
from evennia.utils import logger
from django.conf import settings
import script_conditions
import script_actions


re_words = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)|("(.*?)")')
re_args = re.compile(r'env\["([a-zA-Z_][a-zA-Z0-9_]*)"\]\(')
def safe_statement(statement):
    """
    Add "env." before every words.
    """
    statement = re_words.sub(sub_words, statement)
    statement = re_args.sub(sub_args, statement)
    return statement


statement_keywords = {"not", "and", "or"}
def sub_words(statement):
    """
    Replace "<statement>" with "env.<statement>" except key words.
    """
    statement = statement.group()

    # keep the key words
    if statement in statement_keywords:
        return statement

    # keep the strings in quotes
    if statement[0] == "\"" and statement[-1] == "\"":
        return statement
    
    return "env[\"" + statement + "\"]"


def sub_args(statement):
    """
    Replace "<statement>(" with "<statement>(character, obj, ".
    """
    statement = statement.group()
    return statement + "character, obj, "


class ScriptHandler(object):
    """
    Loads and handles condition scripts and action scripts.
    """

    conditions = {}
    actions = {}


    def __init__(self):
        """
        Creates a script handler instance. Loads scripts.
        """
        self.at_handler_creation()


    def at_handler_creation(self):
        """
        Init script handler, load default scripts.
        """
        pass


    def add_condition(self, key, condition):
        """
        Add a new condition.
        args:
            key (string): the key of the condition.
            condition (function): a function of type func_name(caller, obj, *args)
        """
        self.conditions[key] = condition


    def add_action(self, key, action):
        """
        Add a new condition.
        args:
            key (string): the key of the condition.
            condition (function): a function of type func_name(caller, obj, *args)
        """
        self.actions[key] = action


    def match_condition(self, character, obj, condition):
        """
        Check condition.
        
        Condition is a logical expression. All available conditions are listed in self.conditions.
        """
        if not condition:
            return True

        # add "env." to condition
        condition = safe_statement(condition)

        try:
            # check it
            env_local = {"env": self.conditions,
                         "character": character,
                         "obj": obj}
            match = eval(condition, {}, env_local)
        except Exception, e:
            logger.log_errmsg("match_condition error:%s %s" % (condition, e))
            return False

        return match


    def do_action(self, character, obj, action):
        """
        do action
        
        All available actions are listed in self.actions.
        """
        if not action:
            return

        # add "caller" to action
        action = safe_statement(action)

        # run action
        try:
            env_local = {"env": self.actions,
                         "character": character,
                         "obj": obj}
            exec(action, {}, env_local)
        except Exception, e:
            logger.log_tracemsg("do_action error:%s %s" % (action, e))
            
        return


class ScriptHandlerDefault(ScriptHandler):
    """
    Default script handler.
    """
    def at_handler_creation(self):
        """
        Init script handler, load default scripts.
        """
        self.add_condition("is_quest_in_progress", script_conditions.is_quest_in_progress)
        self.add_condition("can_provide_quest", script_conditions.can_provide_quest)
        self.add_condition("is_quest_finished", script_conditions.is_quest_finished)
        self.add_condition("have_object", script_conditions.have_object)
        self.add_condition("get_attr", script_actions.get_attr)
        self.add_condition("has_attr", script_conditions.has_attr)
        self.add_condition("is_attr", script_conditions.is_attr)

        self.add_action("learn_skill", script_actions.learn_skill)
        self.add_action("give_objects", script_actions.give_objects)
        self.add_action("remove_objects", script_actions.remove_objects)
        self.add_action("teleport_to", script_actions.teleport_to)
        self.add_action("set_attr", script_actions.set_attr)
        self.add_action("get_attr", script_actions.get_attr)
        self.add_action("remove_attr", script_actions.remove_attr)

