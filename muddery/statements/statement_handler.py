"""
This model handle statements.
"""

import re
import traceback
from evennia.utils import logger
from evennia.utils.utils import class_from_module
from django.conf import settings


re_words = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)|("(.*?)")')
def get_safe_statement(statement):
    """
    Add "func." before every words.
    """
    statement = re_words.sub(sub_words, statement)
    return statement


statement_keywords = {"not", "and", "or"}
def sub_words(statement):
    """
    Replace "<statement>" with "func.<statement>" except key words.
    """
    statement = statement.group()

    # keep the key words
    if statement in statement_keywords:
        return statement

    # keep the strings in quotes
    if statement[0] == "\"" and statement[-1] == "\"":
        return statement
    
    return "func(\"" + statement + "\")"


def statement_parser(caller, obj, const):
    """
    Parser statement functions in a statement.

    Args:
        caller: (object) statement's caller
        obj: (object) caller's target
        const: (boolean) whether the statement can keep the caller's status const

    Returns:
        statement function's creator
    """

    def statement_func(func_key):
        """
        Get statement function.

        Args:
            func_key: (string) the key of a statement function

        Returns:
            a function that calls statement function
        """

        def func(*args):
            """
            Calls statement's function.

            Args:
                *args: statement function's args.

            Returns:
                function's return value
            """
            func_class = STATEMENT_HANDLER.statement_set.get_func_class(func_key)
            if not func_class:
                logger.log_errmsg("Statement error: Can not find function: %s." % func_key)
                return

            if const:
                if not func_class.const:
                    logger.log_errmsg("Statement error: \"%s\" is not const." % func_key)
                    return

            func_obj = func_class()
            func_obj.set(caller, obj, args)
            return func_obj.func()

        return func

    return statement_func


class StatementHandler(object):
    """
    Loads and handles condition statements and action statements.
    """
    def __init__(self):
        """
        Creates a statement handler instance. Loads statements.
        """
        # load statements
        statement_set_class = class_from_module(settings.STATEMENT_FUNC_SET)
        self.statement_set = statement_set_class()

    def do_statement(self, caller, obj, statement):
        """
        Do a function.

        Args:
            caller: (object) statement's caller
            obj: (object) caller's current target
            statement: (string) statement's statement

        Returns:
            None
        """
        if not statement:
            return

        # translate to safe statement
        safe_statement = get_safe_statement(statement)

        try:
            # do statement
            env_local = {"func": statement_parser(caller, obj, False)}
            exec(safe_statement, {}, env_local)
        except Exception, e:
            logger.log_tracemsg("run function error:%s %s" % (statement, e))
            return None

        return

    def match_condition(self, caller, obj, statement):
        """
        Check a condition.

        Args:
            caller: (object) statement's caller
            obj: (object) caller's current target
            statement: (string) statement's statement

        Returns:
            (boolean) the result of the condition
        """
        if not statement:
            return True

        # add "env." before function's name
        safe_statement = get_safe_statement(statement)

        try:
            # do statement
            env_local = {"func": statement_parser(caller, obj, True)}
            result = eval(safe_statement, {}, env_local)
        except Exception, e:
            logger.log_tracemsg("run function error:%s %s" % (statement, e))
            return False

        return result


STATEMENT_HANDLER = StatementHandler()
