"""
Area

Areas are compose the whole map. Rooms are belongs to areas.

"""

import ast
from django.conf import settings
from django.apps import apps
from muddery.mappings.typeclass_set import TYPECLASS
from muddery.worlddata.dao.image_resources_mapper import IMAGE_RESOURCES
from muddery.utils.localized_strings_handler import _
from evennia.utils import logger


class MudderyArea(TYPECLASS("OBJECT")):
    """
    Areas are compose the whole map. Rooms are belongs to areas.
    """
    typeclass_key = "AREA"
    typeclass_name = _("Area", "typeclasses")
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
                resource_info = IMAGE_RESOURCES.get(resource)
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

