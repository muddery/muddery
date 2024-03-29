"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.statements.statement_handler import STATEMENT_HANDLER
from muddery.server.utils.localized_strings_handler import _
from muddery.server.mappings.element_set import ELEMENT


class MudderyLockedExit(ELEMENT("EXIT")):
    """
    Characters must unlock these exits to pass it.
    The view and commands of locked exits are different from unlocked exits.
    """
    element_type = "LOCKED_EXIT"
    element_name = "Locked Exit"
    model_name = "exit_locks"

    async def can_traverse(self, character):
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
        if not await super(MudderyLockedExit, self).can_traverse(character):
            return False

        # Only can pass exits which have already been unlocked.
        if await character.is_exit_unlocked(self.get_element_key()):
            if not self.const.unlock_forever:
                # lock the exit again
                character.lock_exit(self.get_element_key())
            return True

        if self.const.auto_unlock and await self.can_unlock(character):
            # Can unlock the exit automatically.
            if self.const.unlock_forever:
                # Unlock it.
                await character.unlock_exit(self.get_element_key())
            return True

        if character.bypass_events():
            return True

        return False

    async def can_unlock(self, caller):
        """
        Unlock an exit.
        """
        # Only can unlock exits which match there conditions.
        return await STATEMENT_HANDLER.match_condition(self.const.unlock_condition, caller, self)

    async def get_conditional_desc(self, caller):
        """
        The particular description for the caller.
        """
        desc = await super(MudderyLockedExit, self).get_conditional_desc(caller)

        if not desc:
            # Get name and description.
            if await caller.is_exit_unlocked(self.get_element_key()):
                # If is unlocked, use common appearance.
                desc = self.const.unlocked_desc
            else:
                desc = self.const.locked_desc

        return desc

    async def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        "args" must be a string without ' and ", usually it is self.id.
        """
        if await caller.is_exit_unlocked(self.get_element_key()):
            # If is unlocked, use common commands.
            return await super(MudderyLockedExit, self).get_available_commands(caller)
        elif not await self.can_unlock(caller):
            return []
        else:
            # show unlock command
            return [{
                "name": self.const.unlock_verb if self.const.unlock_verb else _("Unlock"),
                "cmd": "unlock_exit",
                "args": self.get_element_key()
            }]

