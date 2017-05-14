"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from __future__ import print_function

import traceback
from muddery.utils import utils
from muddery.typeclasses.objects import MudderyObject
from muddery.statements.statement_handler import STATEMENT_HANDLER
from muddery.utils.localized_strings_handler import _
from evennia.utils import logger
from evennia.objects.objects import DefaultExit
from django.conf import settings


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
    def after_data_loaded(self):
        """
        Load exit data.

        Returns:
            None
        """
        super(MudderyExit, self).after_data_loaded()

        # set exit's destination
        self.set_obj_destination(getattr(self.dfield, "destination", None))

        # set action verb
        self.verb = getattr(self.dfield, "verb", _("GOTO"))

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
        # trigger event
        if traversing_object.has_player:
            return self.event.at_character_traverse(traversing_object)
        
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

    def get_name(self):
        """
        Get exit's name.
        """
        if self.name:
            return self.name
        elif self.destination:
            return self.destination.get_name()
        else:
            return ""

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = [{"name":self.verb, "cmd":"goto", "args":self.dbref}]
        return commands


class MudderyReverseExit(MudderyExit):
    """
    This is the reverse side of the two way exit.
    """
    def after_data_loaded(self):
        """
        Called after self.data_loaded().
        """
        self.set_name(getattr(self.dfield, "reverse_name", ""))

        # reverse location and destination
        if not self.location:
            self.set_location(getattr(self.dfield, "destination", ""))

        # set exit's destination
        self.set_obj_destination(getattr(self.dfield, "location", ""))

        self.condition = getattr(self.dfield, "condition", "")

        # set icon
        self.set_icon(getattr(self.dfield, "icon", ""))

    def reset_location(self):
        """
        Set object's location to its default location.

        Returns:
            None
        """
        if hasattr(self.dfield, "destination"):
            self.set_obj_destination(self.dfield.destination)


class MudderyLockedExit(MudderyExit):
    """
    Characters must unlock these exits to pass it.
    The view and commands of locked exits are different from unlocked exits.
    """
    def after_data_loaded(self):
        """
        Set data_info to the object."
        """
        super(MudderyLockedExit, self).after_data_loaded()

        self.unlock_condition = getattr(self.dfield, "unlock_condition", "")
        self.unlock_verb = getattr(self.dfield, "unlock_verb", "")
        self.locked_desc = getattr(self.dfield, "locked_desc", "")
        self.auto_unlock = getattr(self.dfield, "auto_unlock", False)

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
        if not super(MudderyLockedExit, self).at_before_traverse(traversing_object):
            return False

        # Only can pass exits which have already unlockde.
        if traversing_object.is_exit_unlocked(self.get_data_key()):
            return True

        # Show the object's appearance.
        appearance = self.get_appearance(traversing_object)
        traversing_object.msg({"look_obj": appearance})
        return False

    def can_unlock(self, caller):
        """
        Unlock an exit.
        """
        # Only can unlock exits which match there conditions.
        return STATEMENT_HANDLER.match_condition(self.unlock_condition, caller, self)

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        # Get name and description.
        if caller.is_exit_unlocked(self.get_data_key()):
            # If is unlocked, use common appearance.
            return super(MudderyLockedExit, self).get_appearance(caller)

        can_unlock = STATEMENT_HANDLER.match_condition(self.unlock_condition, caller, self)

        if can_unlock and self.auto_unlock:
            # Automatically unlock the exit when a character looking at it.
            caller.unlock_exit(self)
            
            # If is unlocked, use common appearance.
            return super(MudderyLockedExit, self).get_appearance(caller)

        cmds = []
        if can_unlock:
            # show unlock command
            verb = self.unlock_verb
            if not verb:
                verb = _("Unlock")
            cmds = [{"name": verb, "cmd": "unlock_exit", "args": self.dbref}]
        
        info = {"dbref": self.dbref,
                "name": self.name,
                "desc": self.locked_desc,
                "cmds": cmds}
                
        return info

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        if caller.is_exit_unlocked(self.get_data_key()):
            # If is unlocked, use common commands.
            return super(MudderyLockedExit, self).get_available_commands(caller)

        cmds = []
        can_unlock = STATEMENT_HANDLER.match_condition(self.unlock_condition, caller, self)
        if can_unlock:
            # show unlock command
            verb = self.unlock_verb
            if not verb:
                verb = _("Unlock")
            cmds = [{"name": verb, "cmd": "unlock", "args": self.dbref}]

        return cmds
