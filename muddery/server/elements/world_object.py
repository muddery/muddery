"""
Objects that are unique in the whole world.
"""

from muddery.server.mappings.element_set import ELEMENT
from muddery.server.statements.statement_handler import STATEMENT_HANDLER


class MudderyWorldObject(ELEMENT("COMMON_OBJECT")):
    element_type = "WORLD_OBJECT"
    element_name = "World Object"
    model_name = "world_objects"

    async def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.id.
        """
        commands = await super(MudderyWorldObject, self).get_available_commands(caller)

        if self.const.action:
            commands.append({
                "name": self.const.action,
                "cmd": "action",
                "args": self.get_element_key()
            })

        return commands
