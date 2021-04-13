"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _
from muddery.server.statements.statement_handler import STATEMENT_HANDLER


class MudderyWorldObject(ELEMENT("COMMON_OBJECT")):
    element_type = "WORLD_OBJECT"
    element_name = _("World Object", "elements")
    model_name = "world_objects"

    def is_visible(self, caller):
        """
        If this object is visible to the caller.

        Return:
            boolean: visible
        """
        if not self.const.condition:
            return True

        return STATEMENT_HANDLER.match_condition(self.const.condition, caller, self)

    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.id.
        """
        commands = super(MudderyWorldObject, self).get_available_commands(caller)

        if self.const.action:
            commands.append({
                "name": self.const.action,
                "cmd": "action",
                "args": self.get_element_key()
            })

        return commands
