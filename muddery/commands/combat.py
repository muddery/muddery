"""
Battle commands.
"""

from evennia import Command
from evennia import CmdSet
from evennia import default_cmds
from evennia import create_script
from muddery.utils.localized_strings_handler import LS


class CmdHit(Command):
    """
    hit an enemy

    Usage:
      hit <target>

    Strikes the given enemy with your current weapon.
    """
    key = "hit"
    locks = "cmd:all()"
    help_category = "combat"

    def func(self):
        "Implements the command"
        if not self.args:
            self.caller.msg("Usage: hit <target>")
            return 
        target = self.caller.search(self.args)
        if not target:
            return
        ok = self.caller.ndb.combat_handler.add_action("hit", 
                                                       self.caller, 
                                                       target) 
        if ok:
            self.caller.msg("You add 'hit' to the combat queue")
        else:
            self.caller.msg("You can only queue two actions per turn!")

        # tell the handler to check if turn is over
        self.caller.ndb.combat_handler.check_end_turn()


class CmdLook(Command):
    """
    look in combat.

    Usage:
        {"cmd":"look",
         "args":""
        }

    Observes your combat.
    """
    key = "look"
    locks = "cmd:all()"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller

        if not caller.ndb.combat_handler:
            caller.msg({"msg":LS("You are not in combat!")})
            return

        # get combat's appearance
        appearance = caller.ndb.combat_handler.get_appearance()
        caller.msg({"show_combat": appearance})


class CombatCmdSet(CmdSet):
    key = "combat_cmdset"
    mergetype = "Replace"
    priority = 10 
    no_exits = True

    def at_cmdset_creation(self):
        self.add(CmdHit())
        self.add(CmdLook())
