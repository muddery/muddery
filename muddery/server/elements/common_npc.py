"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _


class MudderyCommonNPC(ELEMENT("BASE_NPC")):
    """
    The character not controlled by players.
    """
    element_key = "COMMON_NPC"
    element_name = _("Common NPC", "elements")
    model_name = "common_npcs"
