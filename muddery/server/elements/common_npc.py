"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from muddery.server.mappings.element_set import ELEMENT


class MudderyCommonNPC(ELEMENT("BASE_NPC")):
    """
    The character not controlled by players.
    """
    element_type = "COMMON_NPC"
    element_name = "Common NPC"
    model_name = ""
