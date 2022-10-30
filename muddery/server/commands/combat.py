"""
Battle commands. They only can be used when a character is in a combat.
"""

from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.utils.logger import logger
from muddery.server.utils.localized_strings_handler import _
from muddery.server.commands.command_set import CharacterCmd
from muddery.server.combat.match_pvp import MatchPVPHandler
from muddery.common.utils.defines import CombatType
from muddery.server.combat.combat_handler import COMBAT_HANDLER
from muddery.server.database.worlddata.honour_settings import HonourSettings


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


@CharacterCmd.request("attack")
async def attack(character, args) -> dict or None:
    """
    This will initiate a combat with the target. If the target is
    already in combat, the caller will join its combat.

    Usage:
        {
            "cmd": "attack",
            "args": <object's id>
        }


    """
    if not character.is_alive:
        raise MudderyError(ERR.died, _("You are died."))

    if not args:
        raise MudderyError(ERR.missing_args, _("You should select a target."))

    try:
        target_id = int(args)
        room = character.get_location()
        target = room.get_character(target_id)
    except:
        raise MudderyError(ERR.invalid_input, _("You should select a target."))

    if not character.location or character.location.peaceful:
        raise MudderyError(ERR.invalid_input, _("You can not attack in this place."))

    if not target.is_alive:
        raise MudderyError(ERR.invalid_input, _("%s is died." % target.get_name()))

    if character.location != target.location:
        raise MudderyError(ERR.invalid_input, _("You can not attack %s.") % target.get_name())

    # set up combat
    if character.is_in_combat():
        # caller is in battle
        raise MudderyError(ERR.invalid_input, _("You are in another combat."))

    if target.is_in_combat():
        # target is in battle
        raise MudderyError(ERR.invalid_input, _("%s is in another combat." % target.name))

    # create a new combat
    combat = await COMBAT_HANDLER.create_combat(
        combat_type=CombatType.NORMAL,
        teams={1: [target], 2: [character]},
        desc="",
        timeout=0
    )

    combat_data = {
        "combat_info": combat.get_appearance(),
        "combat_commands": character.get_combat_commands(),
        "combat_states": await combat.get_combat_states(),
        "from": character.get_name(),
        "target": target.get_name(),
    }
    await target.msg({"attack": combat_data})
    return {"attack": combat_data}


@CharacterCmd.request("queue_up_combat")
async def queue_up_combat(character, args) -> dict or None:
    """
    Queue up to make a match between the caller and a proper opponent.

    Usage:
    {
        "cmd": "queue_up_combat",
        "args": None
    }
    """
    honour_settings = HonourSettings.get_first_data()
    if await character.get_level() < honour_settings.min_honour_level:
        raise MudderyError(ERR.invalid_input, _("You need to reach level %s." % honour_settings.min_honour_level))

    await MatchPVPHandler.inst().add(character)


@CharacterCmd.request("quit_combat_queue")
async def quit_combat_queue(character, args) -> dict or None:
    """
    Quit the combat queue.

    Usage:
    {
        "cmd": "quit_combat_queue",
        "args": None
    }
    """
    await MatchPVPHandler.inst().remove(character)
    return


@CharacterCmd.request("confirm_combat")
async def confirm_combat(character, args) -> dict or None:
    """
    Confirm an honour combat.

    Usage:
    {
        "cmd": "confirm_combat",
        "args": None
    }
    """
    MatchPVPHandler.inst().confirm(character)
    return


@CharacterCmd.request("reject_combat")
async def reject_combat(character, args) -> dict or None:
    """
    Reject an honour combat queue.

    Usage:
    {
        "cmd": "reject_combat",
        "args": None
    }
    """
    await MatchPVPHandler.inst().reject(character)
    return


@CharacterCmd.request("get_rankings")
async def get_rankings(character, args) -> dict or None:
    """
    Get top ranking characters.

    Usage:
        {
            "cmd": "get_rankings",
            "args": None
        }
    """
    return await character.get_honour_rankings()
