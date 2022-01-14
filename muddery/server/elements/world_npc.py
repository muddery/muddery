"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from muddery.server.mappings.element_set import ELEMENT
from muddery.server.statements.statement_handler import STATEMENT_HANDLER


class MudderyWorldNPC(ELEMENT("BASE_NPC")):
    """
    The character not controlled by players.
    """
    element_type = "WORLD_NPC"
    element_name = "World NPC"
    model_name = "world_npcs"

    async def after_element_setup(self, first_time):
        """
        Init the character.
        """
        await super(MudderyWorldNPC, self).after_element_setup(first_time)

        if not self.is_temp:
            # if it is dead, reborn at init.
            if not await self.is_alive() and self.reborn_time > 0:
                self.reborn()

    async def is_visible(self, caller):
        """
        If this object is visible to the caller.

        Return:
            boolean: visible
        """
        if not self.const.condition:
            return True

        return await STATEMENT_HANDLER.match_condition(self.const.condition, caller, self)
