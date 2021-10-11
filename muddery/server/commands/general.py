"""
General Character commands usually availabe to all characters

This is adapt from evennia/evennia/commands/default/general.py.
The licence of Evennia can be found in evennia/LICENSE.txt.
"""
import traceback

from django.conf import settings
from evennia.utils import logger
from evennia import create_script
from evennia.comms.models import ChannelDB
from muddery.server.commands.base_command import BaseCommand
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.exception import MudderyError
from muddery.server.utils.defines import ConversationType
from muddery.server.utils.defines import CombatType
from muddery.server.combat.combat_handler import COMBAT_HANDLER
from muddery.server.combat.match_pvp import MATCH_COMBAT_HANDLER
from muddery.server.database.worlddata.honour_settings import HonourSettings
from muddery.server.server import Server


class CmdLook(BaseCommand):
    """
    look around

    Usage:
        {
            "cmd":"look",
        }

    Observes your location or objects in your vicinity.
    """
    key = "look"
    locks = "cmd:all()"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller

        if not caller.is_alive():
            caller.msg({"alert": _("You are died.")})
            return

        # Observes the caller's location
        looking_at_obj = caller.location
        if not looking_at_obj:
            caller.msg({"msg": _("You have nothing to look at!")})
            return

        # Clear caller's target.
        caller.show_location()

        combat = caller.get_combat()
        if combat:
            # If the caller is in combat, add combat info.
            # This happens when a player is in combat and he logout and login again.

            # Send "joined_combat" message first. It will set the player to combat status.
            caller.msg({"joined_combat": True})

            # Send combat infos.
            appearance = combat.get_appearance()
            message = {
                "combat_info": appearance,
                "combat_commands": caller.get_combat_commands(),
            }
            caller.msg(message)


class CmdInventory(BaseCommand):
    """
    observe inventory

    Usage:
        {"cmd":"inventory",
         "args":""
        }
      
    Show everything in your inventory.
    """
    key = "inventory"
    locks = "cmd:all()"

    def func(self):
        "check inventory"
        inv = self.caller.get_inventory_appearance()
        self.caller.msg({"inventory":inv})


class CmdInventoryObject(BaseCommand):
    """
    look at an object in the inventory

    Usage:
        {
            "cmd": "inventory_obj",
            "args": <inventory's position>
        }

    Observes your location or objects in your vicinity.
    """
    key = "inventory_obj"
    locks = "cmd:all()"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        args = self.args

        if not args:
            caller.msg({"alert": _("You should select something in your inventory.")})
            return

        appearance = caller.get_inventory_object_appearance(args)
        if appearance:
            caller.msg({"inventory_obj": appearance}, context=self.context)
        else:
            caller.msg({"alert": _("Can not find it in your inventory.")})


class CmdEquipmentsObject(BaseCommand):
    """
    look at an object in the equipments

    Usage:
        {
            "cmd": "equipments_obj",
            "args": <object's id>
        }

    Observes your location or objects in your vicinity.
    """
    key = "equipments_obj"
    locks = "cmd:all()"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        args = self.args

        if not args:
            caller.msg({"alert": _("You should select something in your equipments.")})
            return

        appearance = caller.return_equipments_object(args)
        if appearance:
            caller.msg({"equipments_obj": appearance}, context=self.context)
        else:
            caller.msg({"alert": _("Can not find it in your equipments.")})


#------------------------------------------------------------
# Say something in the room.
#------------------------------------------------------------
class CmdSay(BaseCommand):
    """
    speak as your character

    Usage:
        {"cmd":"say",
         "args":{"target": <target's id>,
                 "msg": <message>
        }

    Talk to those in your current location.
    """

    key = "say"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Run the say command"

        caller = self.caller

        if not self.args:
            return

        if not "target" in self.args:
            caller.msg({"alert": _("You should choose a target to say.")})
            return

        if not "message" in self.args:
            caller.msg({"alert": _("You should say something.")})
            return

        target_type = self.args["type"]
        target = self.args["target"]
        message = self.args["message"]

        obj = None
        try:
            if target_type == ConversationType.CHANNEL.value:
                obj = ChannelDB.objects.filter(db_key=target)
                obj = obj[0]
            elif target_type == ConversationType.LOCAL.value:
                obj = Server.world.get_room(target)
            elif target_type == ConversationType.PRIVATE.value:
                obj = Server.world.get_character(int(target))
        except Exception as e:
            ostring = "Can not find %s %s: %s" % (target_type, target, e)
            logger.log_tracemsg(ostring)

        if not obj:
            self.msg({"alert": _("You can not talk to it.")})
            return

        obj.get_message(caller, message)


#------------------------------------------------------------
# look at an object in the room
#------------------------------------------------------------
class CmdLookRoomObj(BaseCommand):
    """
    look at an object in the room

    Usage: {
        "cmd": "look_room_obj",
        "args": <object's key>
    }
    """
    key = "look_room_obj"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        caller = self.caller

        if not caller.is_alive():
            caller.msg({"alert": _("You are died.")})
            return

        if not self.args:
            caller.msg({"alert": _("You should appoint an object.")})
            return

        try:
            room = self.caller.get_location()
            obj = room.get_object(self.args)
        except Exception as e:
            caller.msg({"alert": _("Can not find the object.")})
            return

        appearance = obj.get_appearance(caller)
        caller.msg({"look_obj": appearance})


#------------------------------------------------------------
# look at a character in the room
#------------------------------------------------------------
class CmdLookRoomChar(BaseCommand):
    """
    look at a character in the room

    Usage: {
        "cmd": "look_room_char",
        "args": <character's id>
    }
    """
    key = "look_room_char"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        caller = self.caller

        if not caller.is_alive():
            caller.msg({"alert": _("You are died.")})
            return

        if not self.args:
            caller.msg({"alert": _("You should appoint a character.")})
            return

        try:
            char_id = int(self.args)
            room = self.caller.get_location()
            obj = room.get_character(char_id)
        except Exception as e:
            caller.msg({"alert": _("Can not find the object.")})
            return

        appearance = obj.get_appearance(caller)
        caller.msg({"look_obj": appearance})


#------------------------------------------------------------
# traverse an exit
#------------------------------------------------------------
class CmdTraverse(BaseCommand):
    """
    tranvese an exit

    Usage: {
        "cmd": "traverse",
        "args": <exit's key>
    }

    Tranvese an exit, go to the destination of the exit.
    """
    key = "traverse"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Move caller to the exit."
        caller = self.caller

        if not caller.is_alive():
            caller.msg({"alert": _("You are died.")})
            return

        if not self.args:
            caller.msg({"alert": _("Should appoint an exit to go.")})
            return

        try:
            room = self.caller.get_location()
            exit = room.get_exit(self.args)
        except:
            caller.msg({"alert": _("Can not find the exit.")})
            return

        exit.traverse(caller)


#------------------------------------------------------------
# talk to npc
#------------------------------------------------------------
class CmdTalk(BaseCommand):
    """
    Talk to an NPC.

    Usage: {
        "cmd": "talk",
        "args": <NPC's id>
    }

    Begin a talk with an NPC. Show all available dialogues of this NPC.
    """
    key = "talk"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Talk to an NPC."
        caller = self.caller

        if not self.args:
            caller.msg({"alert":_("You should talk to someone.")})
            return

        try:
            npc_id = int(self.args)
            room = self.caller.get_location()
            npc = room.get_character(npc_id)
        except:
            # Can not find the NPC in the caller's location.
            caller.msg({"alert":_("Can not find the one to talk.")})
            return

        caller.talk_to_npc(npc)


#------------------------------------------------------------
# talk to npc
#------------------------------------------------------------

class CmdDialogue(BaseCommand):
    """
    Continue a dialogue.

    Usage:
        {"cmd":"dialogue",
         "args":{"dialogue":<current dialogue>,
                 "npc":<npc's id>,
                }
        }

    Dialogue and sentence refer to the current sentence. This command finishes
    current sentence and get next sentences.
    """
    key = "finish_dialogue"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Continue a dialogue."
        caller = self.caller
        args = self.args

        if not args:
            caller.msg({"alert":_("You should talk to someone.")})
            return

        # Get the dialogue.
        if "dialogue" not in args:
            caller.msg({"alert": _("You should say something.")})
            return
        dlg_key = args["dialogue"]

        try:
            # get NPC
            npc_id = int(args["npc"])
            room = caller.get_location()
            npc = room.get_character(npc_id)
        except:
            npc = None

        caller.finish_dialogue(dlg_key, npc)


#------------------------------------------------------------
# loot objects
#------------------------------------------------------------
class CmdLoot(BaseCommand):
    """
    Loot from a specified object.

    Usage: {
        "cmd": "loot",
        "args": <object's key>
    }

    This command pick out random objects from the loot list and give
    them to the character.
    """
    key = "loot"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Loot objects."
        caller = self.caller

        if not self.args:
            caller.msg({"alert":_("You should loot something.")})
            return

        try:
            room = self.caller.get_location()
            obj = room.get_object(self.args)
        except:
            caller.msg({"alert": _("Can not find the object.")})
            return

        try:
            # do loot
            obj.loot(caller)
        except Exception as e:
            ostring = "Can not loot %s: %s" % (obj.get_element_key(), e)
            logger.log_tracemsg(ostring)
            
        caller.show_location()


#------------------------------------------------------------
# use objects
#------------------------------------------------------------

class CmdUse(BaseCommand):
    """
    Use an object.

    Usage:
        {"cmd":"use",
         "args":<object's id>
        }

    Call caller's use_object function with specified object.
    Different objects can have different results.
    """
    key = "use"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Use an object."
        caller = self.caller

        if not caller.is_alive():
            caller.msg({"alert": _("You are died.")})
            return

        if not self.args or "position" not in self.args:
            caller.msg({"alert": _("You should use something.")})
            return
        position = self.args["position"]

        result = ""
        try:
            # Use the object and get the result.
            result = caller.use_object(int(position))
            caller.show_location()
        except Exception as e:
            ostring = "Can not use %s: %s" % (self.args, e)
            logger.log_tracemsg(ostring)

        # Send result to the player.
        if not result:
            result = _("No result.")

        caller.msg({"alert": result})


#------------------------------------------------------------
# discard objects
#------------------------------------------------------------

class CmdDiscard(BaseCommand):
    """
    Discard an object.

    Usage:
        {"cmd":"discard",
         "args": {
            position: <object's position in the inventory>
        }

    Call caller's remove_objects function with specified object.
    """
    key = "discard"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Use an object."
        caller = self.caller

        if not caller.is_alive():
            caller.msg({"alert":_("You are died.")})
            return

        if not self.args or "position" not in self.args:
            caller.msg({"alert":_("You should discard something.")})
            return
        position = self.args["position"]

        # remove object
        try:
            caller.remove_all_objects_by_position(int(position))
            caller.show_location()
        except Exception as e:
            # If the caller does not have this object.
            caller.msg({"alert": _("Can not discard this object.")})
            logger.log_tracemsg("Can not discard object %s: %s" % (self.args, e))
            return


#------------------------------------------------------------
# put on equipment
#------------------------------------------------------------

class CmdEquip(BaseCommand):
    """
    Put on an equipment.

    Usage:
        {"cmd":"equip",
         "args":<object's id>
        }
    Put on an equipment and add its attributes to the character.
    """
    key = "equip"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Put on an equipment."
        caller = self.caller

        if not self.args or "position" not in self.args:
            caller.msg({"alert": _("You should equip something.")})
            return
        position = self.args["position"]

        try:
            # equip
            caller.equip_object(int(position))
        except Exception as e:
            caller.msg({"alert": _("Can not use this equipment.")})
            logger.log_tracemsg("Can not use equipment %s: %s" % (self.args, e))
            return

        # Send lastest status to the player.
        message = {"alert": _("Equipped!")}
        caller.msg(message)


#------------------------------------------------------------
# take off equipment
#------------------------------------------------------------

class CmdTakeOff(BaseCommand):
    """
    Take off an equipment.

    Usage:
        {"cmd":"takeoff",
         "args":<object's id>
        }
    Take off an equipment and remove its attributes from the character.
    """
    key = "takeoff"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Take off an equipment."
        caller = self.caller

        if not self.args or "position" not in self.args:
            caller.msg({"alert":_("You should take off something.")})
            return
        position = self.args["position"]

        try:
            # Take off the equipment.
            caller.take_off_equipment(position)
        except MudderyError as e:
            caller.msg({"alert": str(e)})
            return
        except Exception as e:
            caller.msg({"alert": _("Can not take off this equipment.")})
            logger.log_tracemsg("Can not take off %s: %s" % (self.args, e))
            return

        # Send lastest status to the player.
        message = {"alert": _("Taken off!")}
        caller.msg(message)


#------------------------------------------------------------
# cast a skill
#------------------------------------------------------------

class CmdCastSkill(BaseCommand):
    """
    Cast a skill when the caller is not in combat.

    Usage:
        {
            "cmd": "cast_skill",
            "args": <skill's key>,
        }
        
        or:

        {
            "cmd": "cast_skill",
            "args":{
                "skill":< skill's key>,
                "target": <skill's target>,
            }
        }
    
    """
    key = "cast_skill"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Cast a skill."
        caller = self.caller
        args = self.args

        if not caller.is_alive():
            caller.msg({"alert":_("You are died.")})
            return

        if caller.is_in_combat():
            caller.msg({"alert": _("You can not cast this skill in a combat.")})
            return

        if not args:
            caller.msg({"alert":_("You should select a skill to cast.")})
            return

        # get skill and target
        skill_key = None
        target = None
        if isinstance(args, str):
            # If the args is a skill's key.
            skill_key = args
        else:
            # If the args is skill's key and target.
            if "skill" not in args:
                caller.msg({"alert":_("You should select a skill to cast.")})
                return
            skill_key = args["skill"]

            # Get target
            try:
                target_id = int(args["target"])
                room = caller.get_location()
                target = room.get_character(target_id)
            except:
                target = None

        try:
            caller.cast_skill(skill_key, target)
        except Exception as e:
            caller.msg({"alert":_("Can not cast this skill.")})
            logger.log_tracemsg("Can not cast skill %s: %s" % (skill_key, e))
            return


#------------------------------------------------------------
# attack a character
#------------------------------------------------------------
class CmdAttack(BaseCommand):
    """
    initiates combat

    Usage:
        {"cmd":"attack",
         "args":<object's id>}
        }

    This will initiate a combat with the target. If the target is
    already in combat, the caller will join its combat.
    """
    key = "attack"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        "Handle command"

        caller = self.caller
        args = self.args

        if not caller:
            return

        if not caller.is_alive():
            caller.msg({"alert":_("You are died.")})
            return

        if not args:
            caller.msg({"alert":_("You should select a target.")})
            return

        try:
            target_id = int(args)
            room = caller.get_location()
            target = room.get_character(target_id)
        except:
            caller.msg({"alert": _("You should select a target.")})
            return

        if not caller.location or caller.location.peaceful:
            caller.msg({"alert": _("You can not attack in this place.")})
            return

        if not target.is_alive():
            caller.msg({"alert": _("%s is died." % target.get_name())})
            return

        if caller.location != target.location:
            caller.msg({"alert": _("You can not attack %s.") % target.get_name()})
            return

        # Set caller's target.
        caller.set_target(target)

        # set up combat
        if caller.is_in_combat():
            # caller is in battle
            message = {"alert": _("You are in another combat.")}
            caller.msg(message)
            return

        if target.is_in_combat():
            # target is in battle
            message = {"alert": _("%s is in another combat." % target.name)}
            caller.msg(message)
            return

        # create a new combat
        try:
            COMBAT_HANDLER.create_combat(
                combat_type=CombatType.NORMAL,
                teams={1: [target], 2: [caller]},
                desc="",
                timeout=0
            )
        except Exception as e:
            logger.log_err("Can not create combat: [%s] %s" % (type(e).__name__, e))
            caller.msg(_("You can not attack %s.") % target.get_name())
            return

        caller.msg(_("You are attacking {R%s{n! You are in combat.") % target.get_name())
        target.msg(_("{R%s{n is attacking you! You are in combat.") % caller.get_name())


# ------------------------------------------------------------
# Queue up for an honour combat.
# ------------------------------------------------------------
class CmdQueueUpCombat(BaseCommand):
    """
    Queue up to make a match between the caller and a proper opponent.

    Usage:
    {"cmd": "queue_up_combat",
     "args": None
    }
    """
    key = "queue_up_combat"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        "Handle command"
        caller = self.caller
        if not caller:
            return

        honour_settings = HonourSettings.get_first_data()
        if caller.get_level() < honour_settings.min_honour_level:
            caller.msg({"alert": _("You need to reach level %s." % honour_settings.min_honour_level)})
            return

        MATCH_COMBAT_HANDLER.add(caller)


# ------------------------------------------------------------
# Queue up for an honour combat.
# ------------------------------------------------------------
class CmdQuitCombatQueue(BaseCommand):
    """
    Quit the combat queue.

    Usage:
    {"cmd": "quit_combat_queue",
     "args": None
    }
    """
    key = "quit_combat_queue"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        "Handle command"

        caller = self.caller
        if not caller:
            return

        MATCH_COMBAT_HANDLER.remove(caller)


# ------------------------------------------------------------
# Confirm an honour combat.
# ------------------------------------------------------------
class CmdConfirmCombat(BaseCommand):
    """
    Confirm an honour combat.

    Usage:
    {"cmd": "confirm_combat",
     "args": None
    }
    """
    key = "confirm_combat"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        "Handle command"

        caller = self.caller
        if not caller:
            return

        MATCH_COMBAT_HANDLER.confirm(caller)


# ------------------------------------------------------------
# Reject an honour combat.
# ------------------------------------------------------------
class CmdRejectCombat(BaseCommand):
    """
    Reject an honour combat queue.

    Usage:
    {"cmd": "reject_combat",
     "args": None
    }
    """
    key = "reject_combat"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        "Handle command"

        caller = self.caller
        if not caller:
            return

        MATCH_COMBAT_HANDLER.reject(caller)


# ------------------------------------------------------------
# Show top rankings
# ------------------------------------------------------------
class CmdGetRankings(BaseCommand):
    """
    Get top ranking characters.

    Usage:
        {"cmd": "get_rankings",
         "args": None
        }
    """
    key = "get_rankings"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        """
        Get characters rankings.

        Returns:
            None
        """
        caller = self.caller
        if not caller:
            return

        caller.show_rankings()


#------------------------------------------------------------
# give up a quest
#------------------------------------------------------------
class CmdGiveUpQuest(BaseCommand):
    """
    Give up a quest.

    Usage:
        {"cmd":"giveup_quest",
         "args":<quest's key>
        }
    """
    key = "giveup_quest"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        """
        Give up a quest.

        Returns:
            None
        """
        caller = self.caller
        if not caller:
            return

        if not self.args:
            caller.msg({"alert":_("You should give up a quest.")})
            return

        quest_key = self.args

        try:
            # Give up the quest.
            caller.quest_handler.give_up(quest_key)
        except MudderyError as e:
            caller.msg({"alert": str(e)})
            return
        except Exception as e:
            caller.msg({"alert": _("Can not give up this quest.")})
            logger.log_tracemsg("Can not give up quest %s: %s" % (quest_key, e))
            return

        # Send lastest status to the player.
        message = {"alert": _("Given up!")}
        caller.msg(message)


#------------------------------------------------------------
# unlock exit
#------------------------------------------------------------
class CmdUnlockExit(BaseCommand):
    """
    Unlock an exit.

    Usage:
        {"cmd":"unlock_exit",
         "args":<object's id>
        }
    A character must unlock a LockedExit before tranvese it.
    """
    key = "unlock_exit"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Open a locked exit."
        caller = self.caller

        if not self.args:
            caller.msg({"alert": _("You should unlock something.")})
            return

        exit_key = self.args

        try:
            # Unlock the exit.
            if not caller.unlock_exit(exit_key):
                caller.msg({"alert": _("Can not open this exit.")})
                return
        except Exception as e:
            caller.msg({"alert": _("Can not open this exit.")})
            logger.log_tracemsg("Can not open exit %s: %s" % (exit_key, e))
            return


#------------------------------------------------------------
# open a shop
#------------------------------------------------------------
class CmdShopping(BaseCommand):
    """
    Open a shop.

    Usage:
        {
            "cmd":"shopping",
            "args": {
                npc: <npc's id>,
                shop: <shop's key>,
            }
        }
    """
    key = "shopping"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Do shopping."
        caller = self.caller
        args = self.args

        if not args or "npc" not in args or "shop" not in args:
            caller.msg({"alert": _("You should shopping in someplace.")})
            return

        shop_key = args["shop"]

        try:
            npc_id = int(args["npc"])
            room = caller.get_location()
            npc = room.get_character(npc_id)
        except:
            caller.msg({"alert": _("Can not find this NPC.")})
            return

        caller.msg({"shop": npc.get_shop_info(shop_key, caller)})


#------------------------------------------------------------
# buy a goods
#------------------------------------------------------------
class CmdBuy(BaseCommand):
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
    key = "buy"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Buy a goods."
        caller = self.caller
        args = self.args

        if not args or "npc" not in args or "shop" not in args or "goods" not in args:
            caller.msg({"alert": _("You should buy something.")})
            return

        try:
            npc_id = int(args["npc"])
            room = self.caller.get_location()
            npc = room.get_character(npc_id)
        except:
            caller.msg({"alert": _("Can not find this NPC.")})
            return

        shop = args["shop"]
        goods = args["goods"]

        # buy goods
        try:
            npc.sell_goods(shop, int(goods), caller)
        except Exception as e:
            traceback.print_exc()
            caller.msg({"alert": _("Can not buy this goods.")})
            logger.log_err("Can not buy %s %s %s: %s" % (args["npc"], shop, goods, e))
            return


class CmdQueryQuest(BaseCommand):
    """
    Query a quest's detail information.

    Usage:
        {
            "cmd": "query_quest",
            "args": {
                "key": <quest's key>
            }
        }

    Observes your location or objects in your vicinity.
    """
    key = "query_quest"
    locks = "cmd:all()"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        args = self.args

        if not args or "key" not in args:
            caller.msg({"alert": _("Can not find it.")})
            return

        quest_key = args["key"]

        try:
            caller.msg({"quest_info": caller.get_quest_info(quest_key)})
        except Exception as e:
            logger.log_err("Can not get %s's quest %s." % (caller.id, quest_key))


class CmdQuerySkill(BaseCommand):
    """
    Query a skill's detail information.

    Usage:
        {
            "cmd": "query_skill",
            "args": {
                "key": <skill's key>
            }
        }

    Observes your location or objects in your vicinity.
    """
    key = "query_skill"
    locks = "cmd:all()"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        args = self.args

        if not args or "key" not in args:
            caller.msg({"alert": _("Can not find it.")})
            return

        skill_key = args["key"]

        try:
            caller.msg({"skill_info": caller.get_skill_info(skill_key)})
        except Exception as e:
            logger.log_err("Can not get %s's skill %s." % (caller.id, skill_key))


#------------------------------------------------------------
# connect
#------------------------------------------------------------
class CmdConnect(BaseCommand):
    """
    Connect to the game when the player has already connectd, 
    ignore it to avoid wrong command messages.

    Usage:
        {"cmd":"connect"}
    """
    key = "connect"
    locks = "cmd:all()"

    def func(self):
        """
        Just ignore it.
        """
        pass


#------------------------------------------------------------
# create
#------------------------------------------------------------
class CmdCreate(BaseCommand):
    """
    create an account when the player has already connectd,
    ignore it to avoid wrong command messages.

    Usage:
        {"cmd":"create_account"}
    """
    key = "create_account"
    locks = "cmd:all()"

    def func(self):
        """
        Just ignore it.
        """
        pass



#------------------------------------------------------------
# create and connect
#------------------------------------------------------------
class CmdCreateConnect(BaseCommand):
    """
    create an account when the player has already connectd,
    ignore it to avoid wrong command messages.

    Usage:
        {"cmd":"create_connect"}
    """
    key = "create_connect"
    locks = "cmd:all()"

    def func(self):
        """
        Just ignore it.
        """
        pass
        
        
#------------------------------------------------------------
# do some tests
#------------------------------------------------------------
class CmdTest(BaseCommand):
    """
    Do some tests.

    Usage:
        {"cmd":"test"}
    """
    key = "test"
    locks = "cmd:all()"

    def func(self):
        """
        Put your test here.
        """
        pass
