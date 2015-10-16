"""
Battle commands.
"""

from evennia import Command
from muddery.utils.localized_strings_handler import LS
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


#------------------------------------------------------------
# cast a skill
#------------------------------------------------------------

class CmdCombatSkill(Command):
    """
    Cast a skill in combat.

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
        caller = self.caller

        if not self.args:
            # No skill info.
            caller.msg({"alert":LS("You should select a skill to cast.")})
            return

        skill_key = None
        target = None
        if isinstance(self.args, basestring):
            # If the args is a skill's key.
            skill_key = self.args
        else:
            # If the args is skill's key and target.
            if not "skill" in self.args:
                # Can not get skill's key.
                caller.msg({"alert":LS("You should select a skill to cast.")})
                return
            skill_key = self.args["skill"]
            target = self.args["target"]

        try:
            # Cast skill.
            # The results of the skill will be sent to relative players
            # by the combat handler.
            result = caller.skill.cast_combat_skill(skill_key, target)
        except Exception, e:
            caller.msg({"msg":LS("Can not cast this skill.")})
            return
