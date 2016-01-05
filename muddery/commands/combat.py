"""
Battle commands.
"""

from evennia import Command
from muddery.utils.localized_strings_handler import LS
from evennia.utils import logger
import traceback


class CmdCombatInfo(Command):
    """
    Get combat info.

    Usage:
        {"cmd":"combat_info",
         "args":""
        }

    Observes your combat.
    """
    key = "combat_info"
    locks = "cmd:all()"

    def func(self):
        """
        Handle the combat info.
        """
        caller = self.caller

        if not caller.is_in_combat():
            # If the caller is not in combat.
            caller.msg({"msg":LS("You are not in combat!")})
            return

        # Get combat's appearance and the character's available commands.
        appearance = caller.ndb.combat_handler.get_appearance()
        message = {"combat_info": appearance,
                   "combat_commands": caller.get_combat_commands()}
        caller.msg(message)
