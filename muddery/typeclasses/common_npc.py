"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from muddery.mappings.typeclass_set import TYPECLASS
from muddery.utils.localized_strings_handler import _


class MudderyCommonNPC(TYPECLASS("BASE_NPC")):
    """
    The character not controlled by players.
    """
    typeclass_key = "COMMON_NPC"
    typeclass_name = _("Common NPC", "typeclasses")
    model_name = "common_npcs"
