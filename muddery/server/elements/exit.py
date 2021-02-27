"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from django.core.exceptions import ObjectDoesNotExist
from evennia.objects.objects import DefaultExit
from evennia.utils import logger
from muddery.server.utils import defines
from muddery.server.utils import utils
from muddery.server.utils.localized_strings_handler import _
from muddery.server.mappings.element_set import ELEMENT


class MudderyExit(ELEMENT("OBJECT"), DefaultExit):
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
    element_type = "EXIT"
    element_name = _("Exit", "elements")
    model_name = "world_exits"

    def after_data_loaded(self):
        """
        Load exit data.

        Returns:
            None
        """
        super(MudderyExit, self).after_data_loaded()

        # set exit's destination
        self.set_obj_destination(self.const.destination)

        # set action verb
        self.verb = self.const.verb if self.const.verb else _("GOTO")

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
        if traversing_object.has_account:
            return self.event.at_character_traverse(traversing_object)
        
        return True

    def at_failed_traverse(self, traversing_object, **kwargs):
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

    def set_obj_destination(self, destination):
        """
        Set object's destination

        Args:
        destination: (string) Destination's name. Must be the key of data info.
        """
        if not destination:
            # remove destination
            self.destination = None
            return

        # set new destination
        try:
            # If has destination, search destination object.
            destination_obj = utils.get_object_by_key(destination)
        except ObjectDoesNotExist:
            logger.log_errmsg("%s can't find destination %s!" % (self.get_object_key(), destination))
            return

        if self.destination == destination_obj:
            # No change.
            return

        if self == destination_obj:
            # Can't set destination to itself.
            logger.log_errmsg("%s can't set destination to itself!" % self.get_object_key())
            return

        self.destination = destination_obj

        if self.destination:
            self.flush_from_cache()

    @classmethod
    def get_event_trigger_types(cls):
        """
        Get an object's available event triggers.
        """
        return [defines.EVENT_TRIGGER_TRAVERSE]

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

