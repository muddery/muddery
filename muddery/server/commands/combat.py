"""
Battle commands. They only can be used when a character is in a combat.
"""

from muddery.server.utils.logger import logger
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

    @classmethod
    async def func(cls, caller, args, context):
        """
        Return the overall combat informations to the caller.
        """
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

    @classmethod
    async def func(cls, caller, args, context):
        """
        Left the current combat.
        """
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

    @classmethod
    async def func(cls, caller, args, context):
        "Cast a skill in a combat."
        if not await caller.is_alive():
            await caller.msg({"alert": _("You are died.")})
            return

        if not caller.is_in_combat():
            await caller.msg({"alert": _("You can only cast this skill in a combat.")})
            return

        if caller.is_auto_cast_skill():
            await caller.msg({"alert": _("You can not cast skills manually.")})
            return

        if not args:
            await caller.msg({"alert": _("You should select a skill to cast.")})
            return

        # get skill and target
        skill_key = None
        target_id = None
        if isinstance(args, str):
            # If the args is a skill's key.
            skill_key = args
        else:
            # If the args is skill's key and target.
            if not "skill" in args:
                await caller.msg({"alert": _("You should select a skill to cast.")})
                return

            skill_key = args["skill"]

            # Get target
            if "target" in args:
                target_id = int(args["target"])

        try:
            # cast this skill.
            await caller.cast_combat_skill(skill_key, target_id)
        except Exception as e:
            await caller.msg({"alert": _("Can not cast this skill.")})
            logger.log_trace("Can not cast skill %s: %s" % (skill_key, e))
            return
