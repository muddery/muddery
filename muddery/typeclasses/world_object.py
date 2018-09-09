"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

from __future__ import print_function

from muddery.mappings.typeclass_set import TYPECLASS
from muddery.utils.localized_strings_handler import _


class MudderyWorldObject(TYPECLASS("OBJECT")):
    typeclass_key = "WORLD_OBJECT"
    typeclass_name = _("World Object", "typeclasses")
