"""
This model handle scripts.
"""

import re
import traceback
from evennia.utils import logger


def match_condition(caller, condition):
    """
    Check condition.
    
    Condition is a logical expression. "caller." will be add before every words
    in the condition, except the ones in quotes.
    
    For example, "hp" will become "caller.hp". So condition can use caller's
    variables and methords in this way.
    
    Condition only can use first level variables, for "db.hp" will become
    "caller.db.caller.hp".
    """
    if not condition:
        return True

    # add "caller." to condition
    condition = safe_statement(condition)

    try:
        # check it
        match = eval(condition, {"caller": caller})
    except Exception, e:
        logger.log_errmsg("match_condition error:%s %s" % (condition, e))
        return False

    return match


def do_action(caller, action):
    """
    do action
    """

    if not action:
        return

    # add "caller" to action
    action = safe_statement(action)

    # run action
    try:
        eval(action, {"caller": caller})
    except Exception, e:
        logger.log_tracemsg("do_dialogue_action error:%s %s" % (action, e))
        
    return


re_words = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)|(\"(.*?)\")")
def safe_statement(statement):
    """
    Add "caller." before every words.
    """
    return re_words.sub(sub_statement, statement)


statement_keywords = {"not", "and", "or"}
def sub_statement(match):
    """
    Replace <match> with caller.<match> except key words.
    """
    match = match.group()

    # keep the key words
    if match in statement_keywords:
        return match

    # keep the strings in quotes
    if match[0] == "\"" and match[-1] == "\"":
        return match

    return "caller." + match
