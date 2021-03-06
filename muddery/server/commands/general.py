"""
General Character commands usually availabe to all characters

This is adapt from evennia/evennia/commands/default/general.py.
The licence of Evennia can be found in evennia/LICENSE.txt.
"""

import math
import random
from django.conf import settings
from evennia.utils import logger
from evennia import create_script
from evennia.comms.models import ChannelDB
from muddery.server.commands.base_command import BaseCommand
from muddery.server.utils.localized_strings_handler import _
from muddery.server.utils.exception import MudderyError
from muddery.server.utils.utils import search_obj_data_key
from muddery.server.utils.defines import ConversationType
from muddery.server.combat.match_pvp_handler import MATCH_COMBAT_HANDLER
from muddery.server.dao.honours_mapper import HONOURS_MAPPER
from muddery.server.dao.honour_settings import HonourSettings
from muddery.server.utils.defines import CombatType


class CmdLook(BaseCommand):
    """
    look at location or object

    Usage:
        {"cmd":"look",
         "args":<object's dbref>
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
        args = self.args

        if not caller.is_alive():
            caller.msg({"alert": _("You are died.")})
            return

        if args:
            # Use search to handle duplicate/nonexistant results.
            looking_at_obj = caller.search_dbref(args)
            if not looking_at_obj:
                caller.msg({"alert": _("Can not find it.")})
                return
        else:
            # Observes the caller's location
            looking_at_obj = caller.location
            if not looking_at_obj:
                caller.msg({"msg": _("You have no location to look at!")})
                return

        if not hasattr(looking_at_obj, 'return_appearance'):
            # this is likely due to us having a player instead
            looking_at_obj = looking_at_obj.character

        if not looking_at_obj.access(caller, "view"):
            # The caller does not have the permission to look.
            caller.msg({"msg": _("Can not find '%s'.") % looking_at_obj.name})
            return

        if looking_at_obj == caller.location:
            # Clear caller's target.
            caller.clear_target()
            caller.show_location()
            
            if caller.is_in_combat():
                # If the caller is in combat, add combat info.
                # This happens when a player is in combat and he logout and login again.

                # Send "joined_combat" message first. It will set the player to combat status.
                caller.msg({"joined_combat": True})
                
                # Send combat infos.
                appearance = caller.ndb.combat_handler.get_appearance()
                message = {"combat_info": appearance,
                           "combat_commands": caller.get_combat_commands()}
                caller.msg(message)
        else:
            # Set caller's target
            caller.set_target(looking_at_obj)

            # Get the object's appearance.
            appearance = looking_at_obj.get_appearance(caller)
            caller.msg({"look_obj": appearance}, context=self.context)

        # the object's at_desc() method.
        looking_at_obj.at_desc(looker=caller)


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
        inv = self.caller.return_inventory()
        self.caller.msg({"inventory":inv})


#------------------------------------------------------------
# Say something in the room.
#------------------------------------------------------------
class CmdSay(BaseCommand):
    """
    speak as your character

    Usage:
        {"cmd":"say",
         "args":{"target": <target's dbref>,
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
            elif target_type == ConversationType.LOCAL.value:
                obj = search_obj_data_key(target)
            elif target_type == ConversationType.PRIVATE.value:
                obj = caller.search_dbref(target)
            obj = obj[0]
        except Exception as e:
            ostring = "Can not find %s %s: %s" % (target_type, target, e)
            logger.log_tracemsg(ostring)

        if not obj:
            self.msg({"alert": _("You can not talk to it.")})
            return

        obj.get_message(caller, message)


#------------------------------------------------------------
# goto exit
#------------------------------------------------------------

class CmdGoto(BaseCommand):
    """
    tranvese an exit

    Usage:
        {"cmd":"goto",
         "args": <exit's dbref> or <direction (n, s, w, e, ne, nw, sw, se)>
        }

    Tranvese an exit, go to the destination of the exit.
    """
    key = "goto"
    locks = "cmd:all()"
    help_cateogory = "General"


    def get_degree(self, from_room, to_room):
        # get the direction's degree of the exit
        # from 0 to 360

        from_area = from_room.location
        to_area = to_room.location

        if from_area.dbref != to_area.dbref:
            return

        from_pos = from_room.position
        to_pos = to_room.position

        if not from_pos or not to_pos:
            return

        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        degree = 0
        if dx == 0:
            if dy < 0:
                degree = 90
            elif dy > 0:
                degree = 270
        else:
            degree = math.atan(-dy / dx) / math.pi * 180
            if dx < 0:
                degree += 180

        return degree

    def get_direction(self, degree):
        if degree is None:
            return

        direction = ""
        degree = degree - math.floor(degree / 360) * 360
        if degree < 22.5:
            direction = "e"
        elif degree < 67.5:
            direction = "ne"
        elif degree < 112.5:
            direction = "n"
        elif degree < 157.5:
            direction = "nw"
        elif degree < 202.5:
            direction = "w"
        elif degree < 247.5:
            direction = "sw"
        elif degree < 292.5:
            direction = "s"
        elif degree < 337.5:
            direction = "se"
        elif degree < 360:
            direction = "e"

        return direction

    def func(self):
        "Move caller to the exit."
        caller = self.caller

        if not caller.is_alive():
            caller.msg({"alert":_("You are died.")})
            return

        if not self.args:
            caller.msg({"alert":_("Should appoint an exit to go.")})
            return

        obj = caller.search_dbref(self.args, location=caller.location)

        if not obj:
            # try to goto direction
            target = self.args.strip().lower()

            if target in {"n", "s", "w", "e", "ne", "nw", "sw", "se"}:
                # get exits in directions
                exits = caller.location.get_exits()
                candidate_exits = []

                from_room = caller.location
                for e in exits:
                    exit_obj = search_obj_data_key(e)
                    if not exit_obj:
                        continue

                    exit_obj = exit_obj[0]
                    to_room = exit_obj.destination
                    degree = self.get_degree(from_room, to_room)
                    direction = self.get_direction(degree)
                    if direction == target:
                        candidate_exits.append(exit_obj)

                if len(candidate_exits) == 1:
                    obj = candidate_exits[0]
                elif len(candidate_exits) > 1:
                    # There is more than one exit in that direction.
                    caller.msg({"alert": _("There is more than one exit in that direction.")})
                    return

        if obj:
            # goto this exit
            if obj.access(self.caller, 'traverse'):
                # we may traverse the exit.
                # MudderyLockedExit handles locks in at_before_traverse().
                if obj.at_before_traverse(self.caller):
                    obj.at_traverse(caller, obj.destination)
            else:
                # exit is locked
                if obj.db.err_traverse:
                    # if exit has a better error message, let's use it.
                    caller.msg({"alert": self.obj.db.err_traverse})
                else:
                    # No shorthand error message. Call hook.
                    obj.at_failed_traverse(caller)
        else:
            # Can not find exit.
            caller.msg({"alert": _("Can not go there.")})
        return


#------------------------------------------------------------
# talk to npc
#------------------------------------------------------------

class CmdTalk(BaseCommand):
    """
    Talk to an NPC.

    Usage:
        {"cmd":"talk",
         "args":<NPC's dbref>
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

        npc = caller.search_dbref(self.args, location=caller.location)
        if not npc:
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
                 "npc":<npc's dbref>,
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

        if not self.args:
            caller.msg({"alert":_("You should talk to someone.")})
            return

        # Get the dialogue.
        if "dialogue" not in self.args:
            caller.msg({"alert": _("You should say something.")})
            return
        dlg_key = self.args["dialogue"]

        npc = None
        if "npc" in self.args and self.args["npc"]:
            # get NPC
            npc = caller.search_dbref(self.args["npc"], location=caller.location)
            if not npc:
                caller.msg({"msg": _("Can not find it.")})
                return

        caller.finish_dialogue(dlg_key, npc)


#------------------------------------------------------------
# loot objects
#------------------------------------------------------------

class CmdLoot(BaseCommand):
    """
    Loot from a specified object.

    Usage:
        {"cmd":"loot",
         "args":<object's dbref>
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

        obj = caller.search_dbref(self.args, location=caller.location)
        if not obj:
            # Can not find the specified object.
            caller.msg({"alert":_("Can not find the object to loot.")})
            return

        try:
            # do loot
            obj.loot(caller)
        except Exception as e:
            ostring = "Can not loot %s: %s" % (obj.get_data_key(), e)
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
         "args":<object's dbref>
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
            caller.msg({"alert":_("You are died.")})
            return

        if not self.args:
            caller.msg({"alert":_("You should use something.")})
            return

        obj = caller.search_dbref(self.args, location=caller)
        if not obj:
            # If the caller does not have this object.
            caller.msg({"alert":_("You don't have this object.")})
            return

        result = ""
        try:
            # Use the object and get the result.
            result = caller.use_object(obj)
            caller.show_location()
        except Exception as e:
            ostring = "Can not use %s: %s" % (obj.get_data_key(), e)
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
         "args":<object's dbref>
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

        if not self.args:
            caller.msg({"alert":_("You should discard something.")})
            return

        obj = caller.search_dbref(self.args, location=caller)
        if not obj:
            # If the caller does not have this object.
            caller.msg({"alert":_("You don't have this object.")})
            return

        # remove used object
        try:
            caller.remove_object(obj.get_data_key(), 1)
            caller.show_location()
        except Exception as e:
            caller.msg({"alert": _("Can not discard this object.")})
            logger.log_tracemsg("Can not discard object %s: %s" % (obj.get_data_key(), e))
            return


#------------------------------------------------------------
# put on equipment
#------------------------------------------------------------

class CmdEquip(BaseCommand):
    """
    Put on an equipment.

    Usage:
        {"cmd":"equip",
         "args":<object's dbref>
        }
    Put on an equipment and add its attributes to the character.
    """
    key = "equip"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Put on an equipment."
        caller = self.caller

        if not self.args:
            caller.msg({"alert": _("You should equip something.")})
            return

        obj = caller.search_dbref(self.args, location=caller)
        if not obj:
            # If the caller does not have this equipment.
            caller.msg({"alert": _("You don't have this equipment.")})
            return

        try:
            # equip
            caller.equip_object(obj)
        except MudderyError as e:
            caller.msg({"alert": str(e)})
            return
        except Exception as e:
            caller.msg({"alert": _("Can not use this equipment.")})
            logger.log_tracemsg("Can not use equipment %s: %s" % (obj.get_data_key(), e))
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
         "args":<object's dbref>
        }
    Take off an equipment and remove its attributes from the character.
    """
    key = "takeoff"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Take off an equipment."
        caller = self.caller

        if not self.args:
            caller.msg({"alert":_("You should take off something.")})
            return

        obj = caller.search_dbref(self.args, location=caller)
        if not obj:
            # If the caller does not have this equipment.
            caller.msg({"alert":_("You don't have this equipment.")})
            return

        try:
            # Take off the equipment.
            caller.take_off_equipment(obj)
        except MudderyError as e:
            caller.msg({"alert": str(e)})
            return
        except Exception as e:
            caller.msg({"alert": _("Can not take off this equipment.")})
            logger.log_tracemsg("Can not take off %s: %s" % (obj.get_data_key(), e))
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
            if "target" in args:
                target = caller.search_dbref(args["target"])

        try:
            caller.cast_skill(skill_key, target)
        except Exception as e:
            caller.msg({"alert":_("Can not cast this skill.")})
            logger.log_tracemsg("Can not cast skill %s: %s" % (skill_key, e))
            return


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
                target = caller.search_dbref(args["target"])

        try:
            # cast this skill.
            caller.cast_combat_skill(skill_key, target)
        except Exception as e:
            caller.msg({"alert": _("Can not cast this skill.")})
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
         "args":<object's dbref>}
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
        if not caller:
            return

        if not caller.is_alive():
            caller.msg({"alert":_("You are died.")})
            return

        if not self.args:
            caller.msg({"alert":_("You should select a target.")})
            return

        target = caller.search_dbref(self.args)
        if not target:
            caller.msg({"alert":_("You should select a target.")})
            return

        if not caller.location or caller.location.peaceful:
            if target.has_account:
                caller.msg({"alert":_("You can not attack in this place.")})
                return

        if not target.is_alive():
            caller.msg({"alert": _("%s is died." % target.get_name())})
            return

        if caller.location != target.location:
            caller.msg({"alert": _("You can not attack %s." % target.get_name())})
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
            # caller is in battle
            message = {"alert": _("%s is in another combat." % target.name)}
            caller.msg(message)
            return

        # create a new combat handler
        chandler = create_script(settings.NORMAL_COMBAT_HANDLER)
        
        # set combat team and desc
        chandler.set_combat(
            combat_type=CombatType.NORMAL,
            teams={1: [target], 2:[caller]},
            desc="",
            timeout=0
        )
        
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
        if caller.db.level < honour_settings.min_honour_level:
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
         "args":<object's dbref>
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
            caller.msg({"alert":_("You should unlock something.")})
            return

        obj = caller.search_dbref(self.args, location=caller.location)
        if not obj:
            caller.msg({"alert":_("Can not find this exit.")})
            return

        try:
            # Unlock the exit.
            if not caller.unlock_exit(obj):
                caller.msg({"alert":_("Can not open this exit.") % obj.name})
                return
        except Exception as e:
            caller.msg({"alert": _("Can not open this exit.")})
            logger.log_tracemsg("Can not open exit %s: %s" % (obj.name, e))
            return

        # The exit may have different appearance after unlocking.
        # Send the lastest appearance to the caller.
        appearance = obj.get_appearance(caller)
        caller.msg({"look_obj": appearance})


#------------------------------------------------------------
# open a shop
#------------------------------------------------------------
class CmdShopping(BaseCommand):
    """
    Open a shop.

    Usage:
        {"cmd":"shopping",
         "args":<shop's dbref>
        }
    """
    key = "shopping"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Do shopping."
        caller = self.caller

        if not self.args:
            caller.msg({"alert":_("You should shopping in someplace.")})
            return

        shop = caller.search_dbref(self.args)
        if not shop:
            caller.msg({"alert":_("Can not find this shop.")})
            return

        shop.show_shop(caller)


#------------------------------------------------------------
# buy a goods
#------------------------------------------------------------
class CmdBuy(BaseCommand):
    """
    Buy a goods.

    Usage:
        {"cmd":"buy",
         "args":<goods' dbref>}
        }
    """
    key = "buy"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Buy a goods."
        caller = self.caller

        if not self.args:
            caller.msg({"alert":_("You should buy something.")})
            return

        goods = caller.search_dbref(self.args)
        if not goods:
            caller.msg({"alert":_("Can not find this goods.")})
            return

        # buy goods
        try:
            goods.sell_to(caller)
        except Exception as e:
            caller.msg({"alert":_("Can not buy this goods.")})
            logger.log_err("Can not buy %s: %s" % (goods.get_data_key(), e))
            return


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
