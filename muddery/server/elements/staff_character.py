"""
Staff Characters

Staff Characters are Objects setup to be puppeted by Staffs.
They can not be seen in game.
"""

from muddery.server.mappings.element_set import ELEMENT


class MudderyStaffCharacter(ELEMENT("PLAYER_CHARACTER")):
    """
    The Character defaults to implementing some of its hook methods with the
    following standard functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead)
    at_after_move - launches the "look" command
    at_pre_puppet - just before Player re-connects, retrieves the character's
                    old location and puts it back on the grid with a "charname
                    has connected" message echoed to the room

    """
    element_type = "STAFF_CHARACTER"
    element_name = "Staff Character"

    def is_staff(self):
        """
        Check if this is a staff character.

        :return:
        """
        return True

    def bypass_events(self):
        """
        Check if this is a staff character.

        :return:
        """
        return True

    def get_appearance(self):
        """
        he common appearance for all players.
        """
        info = super(MudderyStaffCharacter, self).get_appearance()
        info["is_staff"] = True
        return info
