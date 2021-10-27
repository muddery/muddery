"""
Battle commands. They only can be used when a character is in a combat.
"""

from muddery.server.utils import logger
from muddery.server.commands.base_command import BaseCommand
from muddery.server.utils.localized_strings_handler import _


class CmdCombatInfo(BaseCommand):
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
        Return the overall combat informations to the caller.
        """
        caller = self.caller

        if not caller.is_in_combat():
            # If the caller is not in combat.
            caller.msg({"msg":_("You are not in combat!")})
            return

        # Get combat's appearance and the character's available commands.
        appearance = caller.ndb.combat_handler.get_appearance()
        message = {"combat_info": appearance,
                   "combat_commands": caller.get_combat_commands()}
        caller.msg(message)


class CmdLeaveCombat(BaseCommand):
    """
    Get combat info.

    Usage:
        {"cmd":"leave_combat",
         "args":""
        }

    Observes your combat.
    """
    key = "leave_combat"
    locks = "cmd:all()"

    def func(self):
        """
        Left the current combat.
        """
        caller = self.caller

        if not caller.is_in_combat():
            # If the caller is not in combat.
            caller.msg({"msg":_("You are not in combat!")})
            return

        caller.leave_combat()


# ------------------------------------------------------------
# cast a skill in combat
# ------------------------------------------------------------

class CmdCastCombatSkill(BaseCommand):
    """
    Cast a skill when the caller is in combat.

    Usage:
        {
            "cmd": "cast_combat_skill",
            "args": <skill's key>,
        }

        or:

        {
            "cmd": "cast_combat_skill",
            "args":
                {
                    "skill": <skill's key>,
                    "target": <skill's target>,
            }
        }

    """
    key = "cast_combat_skill"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Cast a skill in a combat."
        caller = self.caller
        args = self.args

        if not caller.is_alive():
            caller.msg({"alert": _("You are died.")})
            return

        if not caller.is_in_combat():
            caller.msg({"alert": _("You can only cast this skill in a combat.")})
            return

        if caller.is_auto_cast_skill():
            caller.msg({"alert": _("You can not cast skills manually.")})
            return

        if not args:
            caller.msg({"alert": _("You should select a skill to cast.")})
            return

        # get skill and target
        skill_key = None
        target = None
        if isinstance(args, str):
            # If the args is a skill's key.
            skill_key = args
        else:
            # If the args is skill's key and target.
            if not "skill" in args:
                caller.msg({"alert": _("You should select a skill to cast.")})
                return

            skill_key = args["skill"]

            # Get target
            if "target" in args:
                target_id = int(args["target"])

        try:
            # cast this skill.
            caller.cast_combat_skill(skill_key, target_id)
        except Exception as e:
            caller.msg({"alert": _("Can not cast this skill.")})
            logger.log_trace("Can not cast skill %s: %s" % (skill_key, e))
            return
