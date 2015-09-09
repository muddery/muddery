"""
Battle commands.
"""

from evennia import Command
from muddery.commands import general
from muddery.utils.localized_strings_handler import LS


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
    aliases = ["look"]
    locks = "cmd:all()"

    def func(self):
        """
        Handle the combat info.
        """
        caller = self.caller

        if not caller.ndb.combat_handler:
            caller.msg({"msg":LS("You are not in combat!")})
            return

        # get combat's appearance
        appearance = caller.ndb.combat_handler.get_appearance()
        appearance["commands"] = caller.get_combat_commands()
        caller.msg({"show_combat": appearance})


#------------------------------------------------------------
# cast a skill
#------------------------------------------------------------

class CmdCombatSkill(general.CmdCastSkill):
    """
    Cast a skill.

    Usage:
        {"cmd":"combat_skill",
         "args":<skill's key>}
        }
        
        or:

        {"cmd":"combat_skill",
         "args":{"skill":<skill's key>,
                 "target":<skill's target>}
        }

    """
    key = "combat_skill"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Cast a skill."
        super(CmdCombatSkill, self).func()
        
        # get combat's appearance
        appearance = caller.ndb.combat_handler.get_appearance()
        appearance["commands"] = caller.get_combat_commands()
        caller.msg({"show_combat": appearance})
