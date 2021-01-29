
from muddery.server.database import gamedata_models as BaseModels


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


class object_attributes(BaseModels.BaseAttributes):
    """
    Default table of object attributes.
    """
    pass


class player_characters(BaseModels.BaseAttributes):
    pass
