"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

from __future__ import print_function

from muddery.mappings.typeclass_set import TYPECLASS


class WorldObject(TYPECLASS("OBJECT")):
    key = "WORLD_OBJECT"

