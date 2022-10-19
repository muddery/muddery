"""
Battle commands. They only can be used when a character is in a combat.
"""

from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.utils.logger import logger
from muddery.server.commands.base_command import BaseCommand
from muddery.server.utils.localized_strings_handler import _
from muddery.server.commands.command_set import CharacterCmd


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
    async def func(cls, caller, args):
        """
        Return the overall combat information to the caller.
        """
        if not caller.is_in_combat():
            # If the caller is not in combat.
            await caller.msg({"msg":_("You are not in combat!")})
            return

        # Get combat's appearance and the character's available commands.
        appearance = caller.ndb.combat_handler.get_appearance()
        message = {"combat_info": appearance,
                   "combat_commands": caller.get_combat_commands()}
        await caller.msg(message)


@CharacterCmd.request("leave_combat")
async def leave_combat(character, args) -> dict or None:
    """
    Get combat info.

    Usage:
        {
            "cmd":"leave_combat",
            "args":""
        }

    Observes your combat.
    """
    if not character.is_in_combat():
        # If the caller is not in combat.
        raise MudderyError(ERR.invalid_input, _("You are not in combat."))

    results = await character.leave_combat()

    results.update({
        "state": await character.get_state(),
        "location": character.get_location_info(),
        "look_around": character.look_around(),
    })

    return results


@CharacterCmd.request("cast_combat_skill")
async def cast_combat_skill(character, args) -> dict or None:
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
    if not character.is_alive:
        raise MudderyError(ERR.invalid_input, _("You are died."))

    if not character.is_in_combat():
        raise MudderyError(ERR.invalid_input, _("You can only cast this skill in a combat."))

    if character.is_auto_cast_skill():
        raise MudderyError(ERR.invalid_input, _("You can not cast skills manually."))

    if not args:
        raise MudderyError(ERR.missing_args, _("You should select a skill to cast."))

    # get skill and target
    target_id = None
    if isinstance(args, str):
        # If the args is a skill's key.
        skill_key = args
    else:
        # If the args is skill's key and target.
        if "skill" not in args:
            raise MudderyError(ERR.missing_args, _("You should select a skill to cast."))

        skill_key = args["skill"]

        # Get target
        if "target" in args:
            target_id = int(args["target"])

    # cast this skill.
    return await character.cast_combat_skill(skill_key, target_id)
