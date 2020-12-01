"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

from muddery.server.mappings.brick_set import BRICK
from muddery.server.utils.localized_strings_handler import _


class MudderyWorldObject(BRICK("OBJECT")):
    brick_key = "WORLD_OBJECT"
    brick_name = _("World Object", "bricks")
    model_name = "world_objects"
