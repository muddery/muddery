"""
Area

Areas are compose the whole map. Rooms are belongs to areas.

"""

import ast
from django.conf import settings
from django.apps import apps
from muddery.typeclasses.objects import MudderyObject
from muddery.worlddata.data_sets import DATA_SETS
from evennia.utils import logger


class MudderyArea(MudderyObject):
    """
    Areas are compose the whole map. Rooms are belongs to areas.
    """
    def at_object_creation(self):
        """
        Called once, when this object is first created. This is the
        normal hook to overload for most object types.
        """
        super(MudderyArea, self).at_object_creation()

        self.background = None
        self.background_point = None
        self.corresp_map_pos = None

    def after_data_loaded(self):
        """
        Set data_info to the object.
        """
        super(MudderyArea, self).after_data_loaded()

        # get background
        self.background = None
        resource_key = getattr(self.dfield, "background", None)
        if resource_key:
            try:
                resource_info = DATA_SETS.image_resources.objects.get(key=resource_key)
                self.background = resource_info.resource.name
            except Exception, e:
                logger.log_tracemsg("Load background %s error: %s" % (resource_key, e))

        self.background_point = None
        try:
            # set background point
            background_point = getattr(self.dfield, "background_point", None)
            if background_point:
                self.background_point = ast.literal_eval(background_point)
        except Exception, e:
            logger.log_tracemsg("load background point '%s' error: %s" % (background_point, e))
            
        self.corresp_map_pos = None
        try:
            # set corresponding map position
            corresp_map_pos = getattr(self.dfield, "corresp_map_pos", None)
            if corresp_map_pos:
                self.corresp_map_pos = ast.literal_eval(corresp_map_pos)
        except Exception, e:
            logger.log_tracemsg("load corresponding map position '%s' error: %s" % (corresp_map_pos, e))

    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
        info = super(MudderyArea, self).get_appearance(caller)

        # add background
        info["background"] = getattr(self, "background", None)
        info["background_point"] = getattr(self, "background_point", None)
        info["corresp_map_pos"] = getattr(self, "corresp_map_pos", None)
        
        return info
