"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

import traceback
from muddery.utils import utils
from muddery.typeclasses.objects import MudderyObject
from muddery.utils import script_handler
from muddery.utils.localized_strings_handler import LS
from evennia.utils import logger
from evennia.objects.objects import DefaultExit
from django.conf import settings
from django.db.models.loading import get_model


class MudderyExit(MudderyObject, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_before_traverse(traveller) - called just before traversing.
        at_after_traverse(traveller, source_loc) - called just after traversing.
        at_failed_traverse(traveller) - called if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """
    def at_before_traverse(self, traversing_object):
        """
        Called just before an object uses this object to traverse to
        another object (i.e. this object is a type of Exit)

        Args:
            traversing_object (Object): The object traversing us.

        Notes:
            The target destination should normally be available as
            `self.destination`.
            
            If this method returns False/None, the traverse is cancelled
            before it is even started.

        """
        return True


    def at_failed_traverse(self, traversing_object):
        """
        Overloads the default hook to implement a simple default error message.

        Args:
            traversing_object (Object): The object that failed traversing us.

        Notes:
            Using the default exits, this hook will not be called if an
            Attribute `err_traverse` is defined - this will in that case be
            read for an error string instead.

        """
        traversing_object.msg({"alert": "You cannot go there."})


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        # commands = [{"name":"LOOK", "cmd":"look", "args":self.dbref}]
        verb = getattr(self, "verb", LS("GOTO"))
        if not verb:
            verb = LS("GOTO")
        commands = [{"name":verb, "cmd":"goto", "args":self.dbref}]

        return commands


class MudderyLockedExit(MudderyExit):
    """
    """
    def load_data(self):
        """
        Set data_info to the object."
        """
        super(MudderyLockedExit, self).load_data()

        try:
            model_obj = get_model(settings.WORLD_DATA_APP, settings.EXIT_LOCKS)
            lock_record = model_obj.objects.get(key=self.get_info_key())

            lock = {"condition": lock_record.condition,
                    "verb": lock_record.verb,
                    "message_lock": lock_record.message_lock}
            self.exit_lock = lock
        except Exception, e:
            print "Can't load lock info %s: %s" % (self.get_info_key(), e)


    def at_before_traverse(self, traversing_object):
        """
        Called just before an object uses this object to traverse to
        another object (i.e. this object is a type of Exit)

        Args:
            traversing_object (Object): The object traversing us.

        Notes:
            The target destination should normally be available as
            `self.destination`.
            
            If this method returns False/None, the traverse is cancelled
            before it is even started.

        """
        return traversing_object.is_exit_unlocked(self.get_info_key())


    def can_unlock(self, caller):
        """
        Unlock an exit.
        """
        return script_handler.match_condition(caller, self.exit_lock["condition"])


    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # get name and description
        if caller.is_exit_unlocked(self.get_info_key()):
            return super(MudderyLockedExit, self).get_appearance(caller)

        can_unlock = script_handler.match_condition(caller, self.exit_lock["condition"])
        desc = self.exit_lock["message_lock"]

        cmds = []
        if can_unlock:
            verb = self.exit_lock["verb"]
            if not verb:
                verb = LS("UNLOCK")
            cmds = [{"name":verb, "cmd":"unlock_exit", "args":self.dbref}]
        
        info = {"dbref": self.dbref,
                "name": self.name,
                "desc": desc,
                "cmds": cmds}
                
        return info


    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        if caller.is_exit_unlocked(self.get_info_key()):
            return super(MudderyLockedExit, self).get_available_commands(caller)

        cmds = []
        can_unlock = script_handler.match_condition(caller, self.exit_lock["condition"])
        if can_unlock:
            verb = self.exit_lock["verb"]
            if not verb:
                verb = LS("UNLOCK")
            cmds = [{"name":verb, "cmd":"unlock", "args":self.dbref}]

        return cmds
