"""
This model handle statements.
"""

import re, ast, traceback
from muddery.server.settings import SETTINGS
from muddery.server.utils.logger import logger
from muddery.server.utils.utils import class_from_path
from muddery.server.utils.utils import async_gather, async_wait


re_function = re.compile(r'[a-zA-Z_][a-zA-Z0-9_\.]*\(.*?\)')


async def exec_function(func_set, func_word, caller, obj, **kwargs):
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
        if type(func_args) != tuple:
            func_args = (func_args,)
    except ValueError:
        func_key = func_word
        func_args = ()

    func_class = func_set.get_func_class(func_key)
    if not func_class:
        logger.log_err("Statement error: Can not find function: %s of %s." % (func_key, func_word))
        return

    func_obj = func_class()
    func_obj.set(caller, obj, func_args, **kwargs)
    try:
        return await func_obj.func()
    except Exception as e:
        logger.log_err("Exec function error: %s %s" % (func_word, repr(e)))
        traceback.print_exc()
        return


async def exec_condition(func_set, condition, caller, obj, **kwargs):
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
    matches = re_function.findall(condition)
    if matches:
        results = await async_gather([exec_function(func_set, match, caller, obj, **kwargs) for match in matches])
        values = {
            match: "None" if results[i] is None else "True" if results[i] else "False" for i, match in enumerate(matches)
        }
    else:
        values = {}

    func = get_condition_func(values)
    return re_function.sub(func, condition)


def get_condition_func(values):
    """
    Get a function used in re's sub.

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

        if func_word in values:
            return values[func_word]
        else:
            return "None"

    return function


class StatementHandler(object):
    """
    Loads and handles condition statements and action statements.
    """
    def __init__(self):
        """
        Creates a statement handler instance. Loads statements.
        """
        # load function sets
        action_func_set_class = class_from_path(SETTINGS.ACTION_FUNC_SET)
        self.action_func_set = action_func_set_class()

        condition_func_set_class = class_from_path(SETTINGS.CONDITION_FUNC_SET)
        self.condition_func_set = condition_func_set_class()

        skill_func_set_class = class_from_path(SETTINGS.SKILL_FUNC_SET)
        self.skill_func_set = skill_func_set_class()

    async def do_action(self, action, caller, obj, **kwargs):
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
        if functions:
            await async_wait([exec_function(self.action_func_set, f, caller, obj, **kwargs) for f in functions])

        return

    async def do_skill(self, action, caller, obj, **kwargs):
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
        if functions:
            results = await async_gather([exec_function(self.skill_func_set, f, caller, obj, **kwargs) for f in functions])
        else:
            results = []

        return [r for r in results if r]

    async def match_condition(self, condition, caller, obj, **kwargs):
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
        exec_string = await exec_condition(self.condition_func_set, condition, caller, obj, **kwargs)

        try:
            # do condition
            result = eval(exec_string)
        except Exception as e:
            logger.log_err("Exec condition error: %s %s" % (condition, repr(e)))
            traceback.print_exc()
            return False

        return result


STATEMENT_HANDLER = StatementHandler()
