"""
Commands

Commands describe the input the player can do to the game.

"""

from evennia import Command as BaseCommand
from evennia import default_cmds
from muddery.commands.general import CmdAttack as CmdAttackDefault
from muddery.utils.localized_strings_handler import _


#------------------------------------------------------------
# attack a character
#------------------------------------------------------------
class CmdAttack(CmdAttackDefault):
    """
        initiates combat

        Usage:
        {"cmd":"attack",
        "args":<object's dbref>}
        }

        This will initiate a combat with the target. If the target is
        already in combat, the caller will join its combat.
        Players can not attack in peaceful rooms.
        """
    key = "attack"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        "Handle command"

        caller = self.caller
        if not caller:
            return

        if not caller.is_alive():
            caller.msg({"alert":_("You are died.")})
            return

        if caller.location:
            peaceful = getattr(caller.location.dfield, "peaceful", False)
            if peaceful:
                caller.msg({"alert":_("You can not attack in this place.")})
                return
        
        super(CmdAttack, self).func()
