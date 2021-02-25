"""
Area

Areas are compose the whole map. Rooms are belongs to areas.

"""

from evennia.utils import logger
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.localized_strings_handler import _
from muddery.server.database.dao.image_resource import ImageResource


class MudderyArea(ELEMENT("OBJECT")):
    """
    Areas are compose the whole map. Rooms are belongs to areas.
    """
    element_key = "AREA"
    element_name = _("Area", "elements")
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
        resource = self.const.background
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

