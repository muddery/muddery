"""
None Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from __future__ import print_function

from muddery.mappings.typeclass_set import typeclass_mapping, TYPECLASS


@typeclass_mapping("NON_PLAYER")
class MudderyPlayerCharacter(TYPECLASS("BASE_CHARACTER")):
    """
    The character not controlled by players.
    """
    pass
