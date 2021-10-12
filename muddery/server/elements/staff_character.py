"""
Staff Characters

Staff Characters are Objects setup to be puppeted by Staffs.
They can not be seen in game.
"""

from django.conf import settings
from muddery.server.utils.localized_strings_handler import _
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.game_settings import GAME_SETTINGS


class MudderyStaffCharacter(ELEMENT("PLAYER_CHARACTER")):
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
    element_type = "STAFF_CHARACTER"
    element_name = _("Staff Character", "elements")
    model_name = "staff_characters"

    def is_staff(self):
        """
        Check if this is a staff character.

        :return:
        """
        return True

    def is_visible(self, caller):
        """
        If this object is not visible.

        Return:
            boolean: visible
        """
        return False

    def at_post_puppet(self):
        """
        Called just after puppeting has been completed and all
        Player<->Object links have been established.

        """
        self.available_channels = self.get_available_channels()

        # Send puppet info to the client first.
        output = {
            "id": self.get_id(),
            "name": self.get_name(),
            "is_staff": self.is_staff(),
            "icon": getattr(self, "icon", None),
            "allow_commands": True,
        }

        self.msg({"puppet": output})

        # send character's data to player
        message = {
            "status": self.return_status(),
            "equipments": self.return_equipments(),
            "inventory": self.get_inventory_appearance(),
            "skills": self.return_skills(),
            "quests": self.quest_handler.return_quests(),
            "revealed_map": self.get_revealed_map(),
            "channels": self.available_channels
        }
        self.msg(message)

        self.show_location()

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        info = super(MudderyStaffCharacter, self).get_appearance(caller)
        info["is_staff"] = True
        return info
