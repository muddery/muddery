"""
Area

Areas are compose the whole map. Rooms are belongs to areas.

"""

from evennia.utils import logger
from muddery.server.mappings.brick_set import BRICK
from muddery.server.utils.localized_strings_handler import _
from muddery.server.dao.image_resource import ImageResource


class MudderyArea(BRICK("OBJECT")):
    """
    Areas are compose the whole map. Rooms are belongs to areas.
    """
    brick_key = "AREA"
    brick_name = _("Area", "bricks")
    model_name = "world_areas"

    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
        """
        super(MudderyArea, self).at_object_creation()
        self.background = None

    def after_data_loaded(self):
        """
        Set data_info to the object.
        """
        super(MudderyArea, self).after_data_loaded()

        # get background
        self.background = None
        resource = getattr(self.system, "background", None)
        if resource:
            try:
                resource_info = ImageResource.get(resource)
                resource_info = resource_info[0]
                self.background = {"resource": resource_info.resource,
                                   "width": resource_info.image_width,
                                   "height": resource_info.image_height}
            except Exception as e:
                logger.log_tracemsg("Load background %s error: %s" % (resource, e))

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        info = super(MudderyArea, self).get_appearance(caller)

        # add background
        info["background"] = getattr(self, "background", None)
        
        return info

