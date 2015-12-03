"""
General Character commands usually availabe to all characters

This is adapt from evennia/evennia/commands/default/general.py.
The licence of Evennia can be found in evennia/LICENSE.txt.
"""

from django.conf import settings
from evennia.utils import utils, prettytable, logger
from evennia.commands.command import Command
from evennia.commands.default.muxcommand import MuxCommand
from evennia import create_script
from muddery.utils.dialogue_handler import DIALOGUE_HANDLER
from muddery.utils.localized_strings_handler import LS
import traceback


# limit symbol import for API
__all__ = ("CmdHome", "CmdLook", "CmdNick",
           "CmdInventory", "CmdGet", "CmdDrop", "CmdGive",
           "CmdSay", "CmdPose", "CmdAccess", "CmdGoto", "CmdTalk")


class CmdHome(MuxCommand):
    """
    move to your character's home location

    Usage:
      home

    Teleports you to your home location.
    """

    key = "home"
    locks = "cmd:perm(home) or perm(Builders)"
    arg_regex = r"$"

    def func(self):
        "Implement the command"
        caller = self.caller
        home = caller.home
        if not home:
            caller.msg("You have no home!")
        elif home == caller.location:
            caller.msg("You are already home!")
        else:
            caller.move_to(home)
            caller.msg("There's no place like home ...")


class CmdLook(Command):
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
            caller.msg({"alert":LS("You are died.")})
            return

        if args:
            # Use search to handle duplicate/nonexistant results.
            looking_at_obj = caller.search(args)
            if not looking_at_obj:
                return
        else:
            # Observes the caller's location
            looking_at_obj = caller.location
            if not looking_at_obj:
                caller.msg({"msg":LS("You have no location to look at!")})
                return

        if not hasattr(looking_at_obj, 'return_appearance'):
            # this is likely due to us having a player instead
            looking_at_obj = looking_at_obj.character

        if not looking_at_obj.access(caller, "view"):
            # The caller does not have the permission to look.
            caller.msg({"msg":LS("Could not find '%s'.") % looking_at_obj.name})
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
            caller.msg({"look_obj": appearance})

        # the object's at_desc() method.
        looking_at_obj.at_desc(looker=caller)


class CmdNick(MuxCommand):
    """
    define a personal alias/nick

    Usage:
      nick[/switches] <nickname> = [<string>]
      alias             ''

    Switches:
      object   - alias an object
      player   - alias a player
      clearall - clear all your aliases
      list     - show all defined aliases (also "nicks" works)

    Examples:
      nick hi = say Hello, I'm Sarah!
      nick/object tom = the tall man

    A 'nick' is a personal shortcut you create for your own use. When
    you enter the nick, the alternative string will be sent instead.
    The switches control in which situations the substitution will
    happen. The default is that it will happen when you enter a
    command. The 'object' and 'player' nick-types kick in only when
    you use commands that requires an object or player as a target -
    you can then use the nick to refer to them.

    Note that no objects are actually renamed or changed by this
    command - the nick is only available to you. If you want to
    permanently add keywords to an object for everyone to use, you
    need build privileges and to use the @alias command.
    """
    key = "nick"
    aliases = ["nickname", "nicks", "@nick", "alias"]
    locks = "cmd:all()"

    def func(self):
        "Create the nickname"

        caller = self.caller
        switches = self.switches
        nicks = caller.nicks.get(return_obj=True)

        if 'list' in switches:
            table = prettytable.PrettyTable(["{wNickType",
                                             "{wNickname",
                                             "{wTranslates-to"])
            for nick in utils.make_iter(nicks):
                table.add_row([nick.db_category, nick.db_key, nick.db_strvalue])
            string = "{wDefined Nicks:{n\n%s" % table
            caller.msg(string)
            return
        if 'clearall' in switches:
            caller.nicks.clear()
            caller.msg("Cleared all aliases.")
            return
        if not self.args or not self.lhs:
            caller.msg("Usage: nick[/switches] nickname = [realname]")
            return
        nick = self.lhs
        real = self.rhs

        if real == nick:
            caller.msg("No point in setting nick same as the string to replace...")
            return

        # check so we have a suitable nick type
        if not any(True for switch in switches if switch in ("object", "player", "inputline")):
            switches = ["inputline"]
        string = ""
        for switch in switches:
            oldnick = caller.nicks.get(key=nick, category=switch)
            if not real:
                # removal of nick
                if oldnick:
                    # clear the alias
                    string += "\nNick '%s' (= '%s') was cleared." % (nick, oldnick)
                    caller.nicks.delete(nick, category=switch)
                else:
                    string += "\nNo nick '%s' found, so it could not be removed." % nick
            else:
                # creating new nick
                if oldnick:
                    string += "\nNick %s changed from '%s' to '%s'." % (nick, oldnick, real)
                else:
                    string += "\nNick set: '%s' = '%s'." % (nick, real)
                caller.nicks.add(nick, real, category=switch)
        caller.msg(string)


class CmdInventory(MuxCommand):
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


class CmdGet(MuxCommand):
    """
    pick up something

    Usage:
      get <obj>

    Picks up an object from your location and puts it in
    your inventory.
    """
    key = "get"
    aliases = "grab"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        "implements the command."

        caller = self.caller

        if not self.args:
            caller.msg("Get what?")
            return
        #print "general/get:", caller, caller.location, self.args, caller.location.contents
        obj = caller.search(self.args, location=caller.location)
        if not obj:
            return
        if caller == obj:
            caller.msg("You can't get yourself.")
            return
        if not obj.access(caller, 'get'):
            if obj.db.get_err_msg:
                caller.msg(obj.db.get_err_msg)
            else:
                caller.msg("You can't get that.")
            return

        obj.move_to(caller, quiet=True)
        caller.msg("You pick up %s." % obj.name)
        caller.location.msg_contents("%s picks up %s." %
                                        (caller.name,
                                         obj.name),
                                     exclude=caller)
        # calling hook method
        obj.at_get(caller)


class CmdDrop(MuxCommand):
    """
    drop something

    Usage:
      drop <obj>

    Lets you drop an object from your inventory into the
    location you are currently in.
    """

    key = "drop"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        "Implement command"

        caller = self.caller
        if not self.args:
            caller.msg("Drop what?")
            return

        # Because the DROP command by definition looks for items
        # in inventory, call the search function using location = caller
        obj = caller.search(self.args, location=caller,
                            nofound_string="You aren't carrying %s." % self.args,
                            multimatch_string="You carry more than one %s:" % self.args)
        if not obj:
            return

        obj.move_to(caller.location, quiet=True)
        caller.msg("You drop %s." % (obj.name,))
        caller.location.msg_contents("%s drops %s." %
                                         (caller.name, obj.name),
                                     exclude=caller)
        # Call the object script's at_drop() method.
        obj.at_drop(caller)


class CmdGive(MuxCommand):
    """
    give away something to someone

    Usage:
      give <inventory obj> = <target>

    Gives an items from your inventory to another character,
    placing it in their inventory.
    """
    key = "give"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        "Implement give"

        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: give <inventory object> = <target>")
            return
        to_give = caller.search(self.lhs, location=caller,
                                nofound_string="You aren't carrying %s." % self.lhs,
                                multimatch_string="You carry more than one %s:" % self.lhs)
        target = caller.search(self.rhs)
        if not (to_give and target):
            return
        if target == caller:
            caller.msg("You keep %s to yourself." % to_give.key)
            return
        if to_give.location != caller:
            caller.msg("You are not holding %s." % to_give.key)
            return
        # give object
        caller.msg("You give %s to %s." % (to_give.key, target.key))
        to_give.move_to(target, quiet=True)
        target.msg("%s gives you %s." % (caller.key, to_give.key))


class CmdSay(MuxCommand):
    """
    speak as your character

    Usage:
      say <message>

    Talk to those in your current location.
    """

    key = "say"
    aliases = ['"', "'"]
    locks = "cmd:all()"

    def func(self):
        "Run the say command"

        caller = self.caller

        if not self.args:
            caller.msg("Say what?")
            return

        speech = self.args

        # calling the speech hook on the location
        speech = caller.location.at_say(caller, speech)

        # Feedback for the object doing the talking.
        caller.msg('You say, "%s{n"' % speech)

        # Build the string to emit to neighbors.
        emit_string = '%s says, "%s{n"' % (caller.name,
                                               speech)
        caller.location.msg_contents(emit_string,
                                     exclude=caller)


class CmdPose(MuxCommand):
    """
    strike a pose

    Usage:
      pose <pose text>
      pose's <pose text>

    Example:
      pose is standing by the wall, smiling.
       -> others will see:
      Tom is standing by the wall, smiling.

    Describe an action being taken. The pose text will
    automatically begin with your name.
    """
    key = "pose"
    aliases = [":", "emote"]
    locks = "cmd:all()"

    def parse(self):
        """
        Custom parse the cases where the emote
        starts with some special letter, such
        as 's, at which we don't want to separate
        the caller's name and the emote with a
        space.
        """
        args = self.args
        if args and not args[0] in ["'", ",", ":"]:
            args = " %s" % args.strip()
        self.args = args

    def func(self):
        "Hook function"
        if not self.args:
            msg = "What do you want to do?"
            self.caller.msg(msg)
        else:
            msg = "%s%s" % (self.caller.name, self.args)
            self.caller.location.msg_contents(msg)


class CmdAccess(MuxCommand):
    """
    show your current game access

    Usage:
      access

    This command shows you the permission hierarchy and
    which permission groups you are a member of.
    """
    key = "access"
    aliases = ["groups", "hierarchy"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        "Load the permission groups"

        caller = self.caller
        hierarchy_full = settings.PERMISSION_HIERARCHY
        string = "\n{wPermission Hierarchy{n (climbing):\n %s" % ", ".join(hierarchy_full)
        #hierarchy = [p.lower() for p in hierarchy_full]

        if self.caller.player.is_superuser:
            cperms = "<Superuser>"
            pperms = "<Superuser>"
        else:
            cperms = ", ".join(caller.permissions.all())
            pperms = ", ".join(caller.player.permissions.all())

        string += "\n{wYour access{n:"
        string += "\nCharacter {c%s{n: %s" % (caller.key, cperms)
        if hasattr(caller, 'player'):
            string += "\nPlayer {c%s{n: %s" % (caller.player.key, pperms)
        caller.msg(string)


#------------------------------------------------------------
# goto exit
#------------------------------------------------------------

class CmdGoto(Command):
    """
    tranvese an exit

    Usage:
        {"cmd":"goto",
         "args":<exit's dbref>
        }

    Tranvese an exit, go to the destination of the exit.
    """
    key = "goto"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Move caller to the exit."
        caller = self.caller

        if not caller.is_alive():
            caller.msg({"alert":LS("You are died.")})
            return

        if not self.args:
            caller.msg({"alert":LS("Should appoint an exit to go.")})
            return

        obj = caller.search(self.args, location=caller.location)
        if not obj:
            # Can not find exit.
            caller.msg({"alert":LS("Can not find exit.")})
            return
            
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


#------------------------------------------------------------
# talk to npc
#------------------------------------------------------------

class CmdTalk(Command):
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
            caller.msg({"alert":LS("You should talk to someone.")})
            return

        npc = caller.search(self.args, location=caller.location)
        if not npc:
            # Can not find the NPC in the caller's location.
            caller.msg({"alert":LS("Can not find the one to talk.")})
            return

        # Set caller's target.
        caller.set_target(npc)

        # Get NPC's sentences.
        sentences = DIALOGUE_HANDLER.get_sentences(caller, npc)

        # Get the spearker's name to display.
        speaker = ""
        if sentences:
            speaker = DIALOGUE_HANDLER.get_dialogue_speaker(caller, npc, sentences[0]["speaker"])

        dialogues = []
        for s in sentences:
            dlg = {"speaker": speaker,          # speaker's name
                   "npc": npc.dbref,            # NPC's dbref
                   "dialogue": s["dialogue"],   # dialogue's key
                   "sentence": s["sentence"],   # sentence's ordinal
                   "content": s["content"]}     # sentence's content
            dialogues.append(dlg)

        caller.msg({"dialogue": dialogues})


#------------------------------------------------------------
# talk to npc
#------------------------------------------------------------

class CmdDialogue(Command):
    """
    Continue a dialogue.

    Usage:
        {"cmd":"dialogue",
         "args":{"npc":<npc's dbref>,
                 "dialogue":<current dialogue>,
                 "sentence":<current sentence>}
        }

    Dialogue and sentence refer to the current sentence. This command finishes
    current sentence and get next sentences.
    """
    key = "dialogue"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Continue a dialogue."
        caller = self.caller

        if not self.args:
            caller.msg({"alert":LS("You should talk to someone.")})
            return

        npc = None
        if "npc" in self.args:
            if self.args["npc"]:
                # get NPC
                npc = caller.search(self.args["npc"], location=caller.location)

        # Get the current sentence.
        dialogue = ""
        sentence = 0

        have_current_dlg = False
        try:
            dialogue = self.args["dialogue"]
            sentence = int(self.args["sentence"])
            have_current_dlg = True
        except Exception, e:
            pass

        if have_current_dlg:
            try:
                # Finish current sentence
                DIALOGUE_HANDLER.finish_sentence(caller,
                                                 npc,
                                                 dialogue,
                                                 sentence)
            except Exception, e:
                ostring = "Can not finish sentence %s-%s: %s" % (dialogue, sentence, e)
                logger.log_tracemsg(ostring)

        # Get next sentence.
        sentences = DIALOGUE_HANDLER.get_next_sentences(caller,
                                                        npc,
                                                        dialogue,
                                                        sentence)

        # Get speaker's name.
        speaker = ""
        if sentences:
            speaker = DIALOGUE_HANDLER.get_dialogue_speaker(caller, npc, sentences[0]["speaker"])

        dialogues = []
        for s in sentences:
            dlg = {"speaker": speaker,          # speaker's name
                   "dialogue": s["dialogue"],   # dialogue's key
                   "sentence": s["sentence"],   # sentence's ordinal
                   "content": s["content"]}     # sentence's content
            if npc:
                dlg["npc"] = npc.dbref          # NPC's dbref, if has NPC.

            dialogues.append(dlg)

        # Send dialogues to the player.
        caller.msg({"dialogue": dialogues})


#------------------------------------------------------------
# loot objects
#------------------------------------------------------------

class CmdLoot(Command):
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
            caller.msg({"alert":LS("You should loot something.")})
            return

        obj = caller.search(self.args, location=caller.location)
        if not obj:
            # Can not find the specified object.
            caller.msg({"alert":LS("Can not find the object to loot.")})
            return

        try:
            # do loot
            obj.loot(caller)
        except Exception, e:
            ostring = "Can not loot %s: %s" % (obj.get_info_key(), e)
            logger.log_tracemsg(ostring)


#------------------------------------------------------------
# use objects
#------------------------------------------------------------

class CmdUse(Command):
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
            caller.msg({"alert":LS("You are died.")})
            return

        if not self.args:
            caller.msg({"alert":LS("You should use something.")})
            return

        obj = caller.search(self.args, location=caller)
        if not obj:
            # If the caller does not have this object.
            caller.msg({"alert":LS("You don't have this object.")})
            return

        result = ""
        try:
            # Use the object and get the result.
            result = caller.use_object(obj)
        except Exception, e:
            ostring = "Can not use %s: %s" % (obj.get_info_key(), e)
            logger.log_tracemsg(ostring)

        # Send result to the player.
        if not result:
            result = LS("No result.")
        caller.msg({"alert":result})


#------------------------------------------------------------
# put on equipment
#------------------------------------------------------------

class CmdEquip(Command):
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
            caller.msg({"alert":LS("You should equip something.")})
            return

        obj = caller.search(self.args, location=caller)
        if not obj:
            # If the caller does not have this equipment.
            caller.msg({"alert":LS("You don't have this equipment.")})
            return

        try:
            # equip
            if not caller.equip_object(obj):
                return
        except Exception, e:
            caller.msg({"alert":LS("Can not equip %s.") % obj.name})
            return

        # Send lastest status to the player.
        message = {"alert": LS("Equipped!"),
                   "status": caller.return_status(),
                   "equipments": caller.return_equipments(),
                   "inventory": caller.return_inventory()}
        caller.msg(message)


#------------------------------------------------------------
# take off equipment
#------------------------------------------------------------

class CmdTakeOff(Command):
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
            caller.msg({"alert":LS("You should take off something.")})
            return

        obj = caller.search(self.args, location=caller)
        if not obj:
            # If the caller does not have this equipment.
            caller.msg({"alert":LS("You don't have this equipment.")})
            return

        try:
            # Take off the equipment.
            caller.take_off_object(obj)
        except Exception, e:
            caller.msg({"alert":LS("Can not take off %s.") % obj.name})
            logger.log_tracemsg("Can not take off %s: %s" % (obj.name, e))
            return

        # Send lastest status to the player.
        message = {"alert": LS("Took off!"),
                   "status": caller.return_status(),
                   "equipments": caller.return_equipments(),
                   "inventory": caller.return_inventory()}
        caller.msg(message)


#------------------------------------------------------------
# cast a skill
#------------------------------------------------------------

class CmdCastSkill(Command):
    """
    Cast a skill when the caller is not in combat.

    Usage:
        {"cmd":"castskill",
         "args":<skill's key>}
        }
        
        or:

        {"cmd":"castskill",
         "args":{"skill":<skill's key>,
                 "target":<skill's target>}
        }
    
    """
    key = "castskill"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        "Cast a skill."
        caller = self.caller

        if not caller.is_alive():
            caller.msg({"alert":LS("You are died.")})
            return

        if not self.args:
            caller.msg({"alert":LS("You should select a skill to cast.")})
            return

        skill_key = None
        if isinstance(self.args, basestring):
            # If the args is a skill's key.
            skill_key = self.args
        else:
            # If the args is skill's key and target.
            if not "skill" in self.args:
                caller.msg({"alert":LS("You should select a skill to cast.")})
                return
            skill_key = self.args["skill"]

        # Get target
        target = None
        if "target" in self.args:
            target = caller.search(self.args["target"])

        try:
            # Cast skill.
            caller.cast_skill_manually(skill_key, target)
        except Exception, e:
            caller.msg({"alert":LS("Can not cast this skill.")})
            return


#------------------------------------------------------------
# attack a character
#------------------------------------------------------------
class CmdAttack(Command):
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
            caller.msg({"alert":LS("You are died.")})
            return

        if not self.args:
            caller.msg({"alert":LS("You should select a target.")})
            return

        target = caller.search(self.args)
        if not target:
            caller.msg({"alert":LS("You should select a target.")})
            return

        if not target.is_alive():
            caller.msg({"alert":LS("%s is died." % target.get_name())})
            return

        if caller.location != target.location:
            caller.msg({"alert":LS("You can not attack %s." % target.get_name())})
            return

        # Set caller's target.
        caller.set_target(target)

        # set up combat
        if caller.is_in_combat():
            # caller is in battle
            message = {"alert": LS("You are already in a combat.")}
            caller.msg(message)
            return

        if target.is_in_combat():
            # caller is in battle
            message = {"alert": LS("%s is already in a combat." % target.name)}
            caller.msg(message)
            return

        # create a new combat handler
        chandler = create_script("combat_handler.CombatHandler")
        
        # set combat team and desc
        chandler.set_combat({1: [target], 2:[self.caller]}, "")
        
        self.caller.msg("You attack %s! You are in combat." % target)
        target.msg("%s attacks you! You are in combat." % self.caller)


#------------------------------------------------------------
# unlock exit
#------------------------------------------------------------

class CmdUnlockExit(Command):
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
        "Take off an equipment."
        caller = self.caller

        if not self.args:
            caller.msg({"alert":LS("You should unlock something.")})
            return

        obj = caller.search(self.args, location=caller)
        if not obj:
            caller.msg({"alert":LS("Can not find this exit.")})
            return

        try:
            # Unlock the exit.
            if not caller.unlock_exit(obj):
                caller.msg({"alert":LS("Can not open this exit.") % obj.name})
                return
        except Exception, e:
            caller.msg({"alert": LS("Can not open this exit.")})
            logger.log_tracemsg("Can not open exit %s: %s" % (obj.name, e))
            return

        # The exit may have different appearance after unlocking.
        # Send the lastest appearance to the caller.
        appearance = obj.get_appearance(caller)
        caller.msg({"look_obj": appearance})


#------------------------------------------------------------
# cast a skill
#------------------------------------------------------------

class CmdCombatSkill(Command):
    """
    The skill command in combat, ignore it to avoid wrong command messages.
    """
    key = "combat_skill"
    locks = "cmd:all()"
    help_cateogory = "General"

    def func(self):
        """
        If the character is not in combat, ignore this command.
        """
        pass


#------------------------------------------------------------
# connect
#------------------------------------------------------------
class CmdConnect(Command):
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
class CmdCreate(Command):
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
class CmdCreateConnect(Command):
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
