
from muddery.server.database import gamedata_models as BaseModels


# ------------------------------------------------------------
#
# Object's element key.
#
# ------------------------------------------------------------
class object_element_key(BaseModels.object_element_key):
    pass


# ------------------------------------------------------------
#
# Game object's runtime attributes.
#
# ------------------------------------------------------------
class object_status(BaseModels.object_status):
    pass


# ------------------------------------------------------------
#
# The game's runtime data.
#
# ------------------------------------------------------------
class honours(BaseModels.honours):
    """
    Character's honour data.
    """
    pass
