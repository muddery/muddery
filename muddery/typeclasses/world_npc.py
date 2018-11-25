"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from __future__ import print_function

from muddery.mappings.typeclass_set import TYPECLASS
from muddery.utils.localized_strings_handler import _


class MudderyWorldNPC(TYPECLASS("NPC")):
    """
    The character not controlled by players.
    """
    typeclass_key = "WORLD_NPC"
    typeclass_name = _("World NPC", "typeclasses")
    model_name = "world_npcs"
