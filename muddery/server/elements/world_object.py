"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _


class MudderyWorldObject(ELEMENT("OBJECT")):
    element_key = "WORLD_OBJECT"
    element_name = _("World Object", "elements")
    model_name = "world_objects"

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.dbref.
        """
        commands = super(MudderyWorldObject, self).get_available_commands(caller)

        if self.const.action:
            commands.append({
                "name": self.const.action,
                "cmd": "action",
                "args": self.dbref
            })

        return commands
