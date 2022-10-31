"""
General Character commands usually availabe to all characters
"""

import traceback
from muddery.server.utils.logger import logger
from muddery.common.utils.utils import async_wait
from muddery.server.utils.localized_strings_handler import _
from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.server import Server
from muddery.server.commands.command_set import CharacterCmd


@CharacterCmd.request("look_around")
async def look_around(character, args) -> dict or None:
    """
    Get surroundings in the room.

    Usage:
        {
            "cmd": "look_around",
        }
    """
    return character.look_around()


@CharacterCmd.request("inventory")
async def inventory(character, args) -> dict or None:
    """
    Observe inventory

    Usage:
        {
            "cmd": "inventory",
        }
      
    Show everything in your inventory.
    """
    return character.get_inventory_appearance()


@CharacterCmd.request("inventory_obj")
async def inventory_obj(character, args) -> dict or None:
    """
    look at an object in the inventory

    Usage:
        {
            "cmd": "inventory_obj",
            "args": <inventory's position>
        }

    Observes your location or objects in your vicinity.
    """
    if not args:
        raise MudderyError(ERR.missing_args, _("You should select something in your inventory."))

    return await character.get_inventory_object_appearance(args)


@CharacterCmd.request("all_equipments")
async def all_equipments(character, args) -> dict or None:
    """
    observe all equipments on the player's body

    Usage:
        {
            "cmd": "equipments",
        }

    Show everything in your equipments.
    """
    return character.get_equipments()


@CharacterCmd.request("equipments_obj")
async def equipments_obj(character, args) -> dict or None:
    """
    look at an object in the equipments

    Usage:
        {
            "cmd": "equipments_obj",
            "args": <object's position>
        }

    Observes your location or objects in your vicinity.
    """
    if not args:
        raise MudderyError(ERR.missing_args, _("You should select something in your equipments."))

    return await character.return_equipments_object(args)


@CharacterCmd.request("say")
async def say(character, args) -> dict or None:
    """
    speak as your character

    Usage:
        {
            "cmd": "say",
            "args": {
                "type": <target's type>,
                "target": <target's id>,
                "msg": <message>
            }
        }

    Talk to those in your current location.
    """
    if not args:
        raise MudderyError(ERR.missing_args, _("You should say something."))

    if "target" not in args:
        raise MudderyError(ERR.missing_args, _("You should choose a target to say."))

    if "message" not in args:
        raise MudderyError(ERR.missing_args, _("You should say something."))

    target_type = args["type"]
    target = args["target"]
    message = args["message"]

    await Server.world.send_message(character, target_type, target, message)

    return


@CharacterCmd.request("look_room_obj")
async def look_room_obj(character, args) -> dict or None:
    """
    look at an object in the room

    Usage:
        {
            "cmd": "look_room_obj",
            "args": <object's key>
        }
    """
    if not character.is_alive:
        raise MudderyError(ERR.died, _("You are died."))

    if not args:
        raise MudderyError(ERR.missing_args, _("You should appoint an object."))

    try:
        room = character.get_location()
        obj = room.get_object(args)
    except Exception as e:
        raise MudderyError(ERR.invalid_input, _("Can not find the object."))

    return await obj.get_detail_appearance(character)


@CharacterCmd.request("look_room_char")
async def look_room_char(character, args) -> dict or None:
    """
    look at a character in the room

    Usage:
        {
            "cmd": "look_room_char",
            "args": <character's id>
        }
    """
    if not character.is_alive:
        raise MudderyError(ERR.died, _("You are died."))

    if not args:
        raise MudderyError(ERR.missing_args, _("You should appoint a character."))

    try:
        char_id = int(args)
        room = character.get_location()
        obj = room.get_character(char_id)
    except Exception as e:
        raise MudderyError(ERR.invalid_input, _("Can not find the character."))

    return await obj.get_detail_appearance(character)


@CharacterCmd.request("traverse")
async def traverse(character, args) -> dict or None:
    """
    traverse an exit

    Usage:
        {
            "cmd": "traverse",
            "args": <exit's key>
        }

    Traverse an exit, go to the destination of the exit.
    """
    if not character.is_alive:
        raise MudderyError(ERR.died, _("You are died."))

    if not args:
        raise MudderyError(ERR.missing_args, _("Should appoint an exit to go."))

    exit_key = args

    try:
        room = character.get_location()
        exit_obj = room.get_exit(exit_key)
    except Exception as e:
        raise MudderyError(ERR.invalid_input, _("Can not find the exit."))

    results = await exit_obj.traverse(character)

    if results["traversed"]:
        # the character moved to the new location
        results.update({
            "location": character.get_location_info()
        })
    else:
        # can not traverse
        results.update({
            "exit": await exit_obj.get_detail_appearance(character)
        })

    return results


@CharacterCmd.request("talk")
async def talk(character, args) -> dict or None:
    """
    Talk to an NPC.

    Usage:
        {
            "cmd": "talk",
            "args": <NPC's id>
        }

    Begin a talk with an NPC. Show all available dialogues of this NPC.
    """
    if not character.is_alive:
        raise MudderyError(ERR.died, _("You are died."))

    if not args:
        raise MudderyError(ERR.missing_args, _("You should talk to someone."))

    try:
        npc_id = int(args)
        room = character.get_location()
        npc = room.get_character(npc_id)
    except Exception as e:
        raise MudderyError(ERR.invalid_input, _("Can not find the character."))

    return await character.talk_to_npc(npc)


@CharacterCmd.request("finish_dialogue")
async def finish_dialogue(character, args) -> dict or None:
    """
    Finish current dialogue.

    Usage:
        {
            "cmd": "finish_dialogue",
            "args": {
                "dialogue": <current dialogue>,
                "npc": <NPC's id>,
            }
        }

    Dialogue and sentence refer to the current sentence. This command finishes
    current sentence and get next sentences.
    """
    if not args:
        raise MudderyError(ERR.missing_args, _("You should talk to someone."))

    # Get the dialogue.
    if "dialogue" not in args:
        raise MudderyError(ERR.missing_args, _("You should say something."))
    dlg_key = args["dialogue"]

    try:
        # get NPC
        npc_id = int(args["npc"])
        room = character.get_location()
        npc = room.get_character(npc_id)
    except:
        npc = None

    return await character.finish_dialogue(dlg_key, npc)


@CharacterCmd.request("loot")
async def loot(character, args) -> dict or None:
    """
    Loot from a specified object.

    Usage:
        {
            "cmd": "loot",
            "args": <object's key>
        }

    This command pick out random objects from the loot list and give
    them to the character.
    """
    if not args:
        raise MudderyError(ERR.missing_args, _("You should loot something."))

    try:
        room = character.get_location()
        obj = room.get_object(args)
    except:
        raise MudderyError(ERR.invalid_input, _("Can not find the object."))

    # loot
    return await obj.loot(character)


@CharacterCmd.request("use")
async def use(character, args) -> dict or None:
    """
    Use an object in the inventory.

    Usage:
        {
            "cmd": "use",
            "args": {
                position: <object's position in the inventory>
            }
        }

    Call caller's use_object function with specified object.
    Different objects can have different results.
    """
    if not character.is_alive:
        raise MudderyError(ERR.died, _("You are died."))

    if not args or "position" not in args:
        raise MudderyError(ERR.missing_args, _("You should use something."))
    position = args["position"]

    # Use the object and get the result.
    return await character.use_object(int(position))


@CharacterCmd.request("discard")
async def discard(character, args) -> dict or None:
    """
    Discard an object in the inventory.

    Usage:
        {
            "cmd":"discard",
            "args": {
                position: <object's position in the inventory>
            }
        }
    """
    if not character.is_alive:
        raise MudderyError(ERR.died, _("You are died."))

    if not args or "position" not in args:
        raise MudderyError(ERR.missing_args, _("You should discard something."))
    position = args["position"]

    # remove object
    await character.remove_all_objects_by_position(int(position))


@CharacterCmd.request("equip")
async def equip(character, args) -> dict or None:
    """
    Put on equipment.

    Usage:
        {
            "cmd": "equip",
            "args": {
                position: <object's position in the inventory>
            }
        }
    Put on equipment and add its attributes to the character.
    """
    if not args or "position" not in args:
        raise MudderyError(ERR.missing_args, _("You should equip something."))

    position = args["position"]

    # equip
    await character.equip_object(int(position))

    return {
        "state": await character.get_state(),
    }


@CharacterCmd.request("takeoff")
async def takeoff(character, args) -> dict or None:
    """
    Take off an equipment and remove its attributes from the character.

    Usage:
        {
            "cmd": "takeoff",
            "args": {
                position: <object's position in the equipments>
            }
        }

    """
    if not args or "position" not in args:
        raise MudderyError(ERR.missing_args, _("You should take off something."))

    position = args["position"]

    # Take off the equipment.
    await character.take_off_equipment(position)

    # Send the latest state to the player.
    return {
        "state": await character.get_state()
    }


@CharacterCmd.request("cast_skill")
async def cast_skill(character, args) -> dict or None:
    """
    Cast a skill when the caller is not in combat.

    Usage:
        {
            "cmd": "cast_skill",
            "args": {
                "skill": <skill's key>,
                "target": <skill's target>,
            }
        }
    
    """
    if not character.is_alive:
        raise MudderyError(ERR.died, _("You are died."))

    if character.is_in_combat():
        raise MudderyError(ERR.invalid_input, _("You can not cast this skill in a combat."))

    if not args:
        raise MudderyError(ERR.missing_args, _("You should select a skill to cast."))

    if "skill" not in args:
        raise MudderyError(ERR.missing_args, _("You should select a skill to cast."))
    skill_key = args["skill"]

    # Get target
    target = None
    if "target" in args and args["target"]:
        try:
            target_id = int(args["target"])
            room = character.get_location()
            target = room.get_character(target_id)
        except:
            raise MudderyError(ERR.invalid_input, _("Can not get the target."))

    return await character.cast_skill(skill_key, target)


@CharacterCmd.request("give_up_quest")
async def give_up_quest(character, args) -> dict or None:
    """
    Give up a quest.

    Usage:
        {
            "cmd": "give_up_quest",
            "args": <quest's key>
        }
    """
    if not args:
        raise MudderyError(ERR.missing_args, _("You should give up a quest."))
    quest_key = args

    # Give up the quest.
    return await character.quest_handler.give_up(quest_key)


@CharacterCmd.request("unlock_exit")
async def unlock_exit(character, args) -> dict or None:
    """
    Unlock a locked exit. A character must unlock a LockedExit before traverse it.

    Usage:
        {
            "cmd": "unlock_exit",
            "args": <exit's key>
        }
    """
    if not args:
        raise MudderyError(ERR.missing_args, _("You should unlock something."))

    exit_key = args

    try:
        room = character.get_location()
        exit_obj = room.get_exit(exit_key)
    except Exception as e:
        raise MudderyError(ERR.invalid_input, _("Can not find the exit."))

    # Unlock the exit.
    if await character.unlock_exit(exit_key):
        # The exit may have different appearance after unlocking.
        # Send the lastest appearance to the caller.
        return {
            "unlocked": True,
            "exit": await exit_obj.get_detail_appearance(character)
        }
    else:
        return {"unlocked": False}


@CharacterCmd.request("shopping")
async def shopping(character, args) -> dict or None:
    """
    Open a shop from a character.

    Usage:
        {
            "cmd": "shopping",
            "args": {
                "npc": <npc's id>,
                "shop": <shop's key>,
            }
        }
    """
    if not args or "npc" not in args or "shop" not in args:
        raise MudderyError(ERR.missing_args, _("You should shopping in someplace."))

    shop_key = args["shop"]

    try:
        npc_id = int(args["npc"])
        room = character.get_location()
        npc = room.get_character(npc_id)
    except:
        raise MudderyError(ERR.invalid_input, _("Can not find this NPC."))

    return await npc.get_shop_info(shop_key, character)


@CharacterCmd.request("buy")
async def buy(character, args) -> dict or None:
    """
    Buy a goods.

    Usage:
        {
            "cmd": "buy",
            "args": {
                "npc": <npc's id>,
                "shop": <shop's key>,
                "goods": <goods' index>,
            }
        }
    """
    if not args or "npc" not in args or "shop" not in args or "goods" not in args:
        raise MudderyError(ERR.missing_args, _("You should buy something."))

    try:
        npc_id = int(args["npc"])
        room = character.get_location()
        npc = room.get_character(npc_id)
    except:
        raise MudderyError(ERR.invalid_input, _("Can not find this NPC."))

    shop = args["shop"]
    goods = args["goods"]

    # buy goods
    return await npc.sell_goods(shop, int(goods), character)


@CharacterCmd.request("all_quests")
async def all_quests(character, args) -> dict or None:
    """
    Query the character's all quests.

    Usage:
        {
            "cmd": "all_quests"
        }
    """
    return await character.get_quests()


@CharacterCmd.request("query_quest")
async def query_quest(character, args) -> dict or None:
    """
    Query a quest's detail information.

    Usage:
        {
            "cmd": "query_quest",
            "args": {
                "key": <quest's key>
            }
        }
    """
    if not args or "key" not in args:
        raise MudderyError(ERR.missing_args, _("Can not find the quest."))

    quest_key = args["key"]

    return await character.get_quest_info(quest_key)


@CharacterCmd.request("all_skills")
async def all_skills(character, args) -> dict or None:
    """
    Query the character's all skills.

    Usage:
        {
            "cmd": "all_skills"
        }
    """
    return character.get_skills()


@CharacterCmd.request("query_skill")
async def query_skill(character, args) -> dict or None:
    """
    Query a skill's detail information.

    Usage:
        {
            "cmd": "query_skill",
            "args": {
                "key": <skill's key>
            }
        }
    """
    if not args or "key" not in args:
        raise MudderyError(ERR.missing_args, _("Can not find the skill."))

    skill_key = args["key"]

    return await character.get_skill_info(skill_key)


@CharacterCmd.request("get_revealed_maps")
async def get_revealed_maps(character, args) -> dict or None:
    """
    Get a character's revealed maps.

    Usage:
        {
            "cmd": "get_revealed_maps"
        }
    """
    return character.get_revealed_maps()
