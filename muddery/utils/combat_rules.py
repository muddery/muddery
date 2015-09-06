"""
Combat rules.
"""

from evennia.utils import logger
import traceback


def resolve_combat(combat_handler, action, character, target):
    """
    This is called by the combat handler
    """
    try:
        hurt = character.attack / (character.attack + target.defence) * character.attack
        target.hurt(hurt)

        # echo results of each subturn
        combat_handler.msg_all({"attacker": character.name,
                                "target": target.name,
                                "hurt": hurt})
    except Exception, e:
        logger.log_errmsg("Combat error: %s" % e)
        logger.log_errmsg(traceback.format_exc())