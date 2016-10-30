"""
This model handle statements.
"""

import re
import ast
import traceback
from evennia.utils import logger
from evennia.utils.utils import class_from_module
from django.conf import settings


#re_words = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)|("(.*)")')
re_function = re.compile(r'[a-zA-Z_][a-zA-Z0-9_\.]*\(.*\)')
def exec_condition(func_set, condition, caller, obj):
    """
    Execute the statements.

    Args:
        func_set: (object) condition function set
        condition: (string) condition statement
        caller: (object) statement's caller
        obj: (object) caller's target

    Returns:
        result
    """
    func = get_condition_func(func_set, caller, obj)
    return re_function.sub(func, condition)


def get_condition_func(func_set, caller, obj):
    """
    Get a function used in re's sub.

    Args:
        func_set: (object) condition function set
        caller: (object) statement's caller
        obj: (object) caller's target

    Returns:
        function
    """
    def function(word):
        """
        Do function.

        Args:
            word: (string) condition function

        Returns:
            (string) "True" or "False"
        """
        func_word = word.group()

        try:
            result = exec_function(func_set, func_word, caller, obj)
        except Exception, e:
            logger.log_errmsg("Exec function error: %s %s" % (function, e))
            result = False

        if result:
            return "True"
        else:
            return "False"

    return function


def exec_function(func_set, func_word, caller, obj):
    """
    Do function.

    Args:
        func_set: (object) function set
        func_word: (string) function string, such as: func("value")
        caller: (object) statement's caller
        obj: (object) caller's target

    Returns:
        function result
    """

    # separate function's key and args
    try:
        pos = func_word.index("(")
        func_key = func_word[:pos]
        func_args = ast.literal_eval(func_word[pos:])
    except ValueError:
        func_key = func_word
        func_args = ()

    func_class = func_set.get_func_class(func_key)
    if not func_class:
        logger.log_errmsg("Statement error: Can not find function: %s." % func_key)
        return

    func_obj = func_class()
    func_obj.set(caller, obj, func_args)
    return func_obj.func()


class StatementHandler(object):
    """
    Loads and handles condition statements and action statements.
    """
    def __init__(self):
        """
        Creates a statement handler instance. Loads statements.
        """
        # load function sets
        action_func_set_class = class_from_module(settings.ACTION_FUNC_SET)
        self.action_func_set = action_func_set_class()

        condition_func_set_class = class_from_module(settings.CONDITION_FUNC_SET)
        self.condition_func_set = condition_func_set_class()

        skill_func_set_class = class_from_module(settings.SKILL_FUNC_SET)
        self.skill_func_set = skill_func_set_class()

    def do_action(self, action, caller, obj):
        """
        Do a function.

        Args:
            action: (string) statements separated by ";"
            caller: (object) statement's caller
            obj: (object) caller's current target

        Returns:
            None
        """
        if not action:
            return

        # execute the statement
        functions = action.split(";")
        for function in functions:
            try:
                exec_function(self.action_func_set, function, caller, obj)
            except Exception, e:
                logger.log_errmsg("Exec function error: %s %s" % (function, e))

        return

    def match_condition(self, condition, caller, obj):
        """
        Check a condition.

        Args:
            condition: (string) a condition expression
            caller: (object) statement's caller
            obj: (object) caller's current target

        Returns:
            (boolean) the result of the condition
        """
        if not condition:
            return True

        # calculate functions first
        exec_string = exec_condition(self.condition_func_set, condition, caller, obj)

        try:
            # do condition
            result = eval(exec_string)
        except Exception, e:
            logger.log_tracemsg("Exec condition error:%s %s" % (condition, e))
            return False

        return result


STATEMENT_HANDLER = StatementHandler()
