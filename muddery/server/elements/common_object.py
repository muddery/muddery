"""
CommonObject is the object that players can put into their inventory.

"""

from muddery.server.mappings.element_set import ELEMENT


class MudderyCommonObject(ELEMENT("MATTER")):
    """
    This is a common object, the base class of all objects..
    """
    element_type = "COMMON_OBJECT"
    element_name = "Common Object"
    model_name = "common_objects"
