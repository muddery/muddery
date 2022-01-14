"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

import traceback
import weakref
from muddery.server.utils.logger import logger
from muddery.server.utils.localized_strings_handler import _
from muddery.server.elements.base_element import BaseElement
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.server import Server


class MudderyExit(BaseElement):
    """
    Exits are connectors between rooms.
    """
    element_type = "EXIT"
    element_name = "Exit"
    model_name = "world_exits"

    def __init__(self):
        """
        Initial the object.
        """
        super(MudderyExit, self).__init__()

        self.destination_obj = None

    async def is_visible(self, caller):
        """
        If this object is visible to the caller.

        Return:
            boolean: visible
        """
        if not self.const.condition:
            return True

        return await STATEMENT_HANDLER.match_condition(self.const.condition, caller, self)

    async def traverse(self, character):
        """
        Traverse to the destination.

        :param character:
        :return:
        """
        if not await self.can_traverse(character):
            await character.msg({"msg": _("You can not pass.")})
            return

        if not self.destination_obj:
            self.destination_obj = weakref.ref(Server.world.get_room(self.const.destination))

        try:
            await character.move_to(self.destination_obj())
        except Exception as e:
            traceback.print_exc()
            logger.log_err("%s cannot set location: (%s)%s." % (character.get_id(), type(e).__name__, e))
            await character.msg({"msg": _("You can not go there.")})

    async def can_traverse(self, character):
        """
        If the character can traverse the exit return True else False.

        :param character:
        :return:
        """
        return True

    def get_name(self):
        """
        Get exit's name.
        """
        if self.const.name:
            return self.const.name
        elif self.const.destination:
            if not self.destination_obj:
                self.destination_obj = weakref.ref(Server.world.get_room(self.const.destination))
            return self.destination_obj().get_name()
        else:
            return _("Exit")

    async def get_desc(self, caller):
        """
        Get the exit's description.
        :param caller:
        :return:
        """
        return _("This is an exit")

    async def get_appearance(self, caller):
        """
        Get the appearance of the exit.
        :param caller:
        :return:
        """
        return {
            "key": self.get_element_key(),
            "name": self.get_name(),
            "desc": await self.get_desc(caller),
            "cmds": await self.get_available_commands(caller),
        }

    async def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.id.
        """
        commands = [{
            "name": self.const.verb if self.const.verb else _("GOTO"),
            "cmd": "traverse",
            "args": self.get_element_key()
        }]
        return commands
