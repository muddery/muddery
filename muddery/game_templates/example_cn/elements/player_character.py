"""
Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.elements.player_character import MudderyPlayerCharacter
from muddery.server.utils.localized_strings_handler import _


class PlayerCharacter(MudderyPlayerCharacter):
    """
    The Character defaults to implementing some of its hook methods with the
    following standard functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_post_puppet(player) -  when Player disconnects from the Character, we
                    store the current location, so the "unconnected" character
                    object does not need to stay on grid but can be given a
                    None-location while offline.
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """
    element_type = "PLAYER_CHARACTER"

    async def cast_skill(self, skill_key, target):
        """
        Cast a skill.

        Args:
            skill_key: (string) skill's key.
            target: (object) skill's target.
        """
        skill_obj = self.skills[skill_key]["obj"]
        skill_mp = skill_obj.get_mp()
        mp = await self.states.load("mp")
        if mp < skill_mp:
            raise MudderyError(ERR.invalid_input, _("Not enough mana to cast {b%s{n!") % skill_obj.get_name())

        return await super(PlayerCharacter, self).cast_skill(skill_key, target)
