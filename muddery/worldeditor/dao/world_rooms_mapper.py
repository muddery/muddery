"""
Query and deal common tables.
"""

from django.apps import apps
from django.conf import settings
from django.db import connections
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.exception import MudderyError, ERR


class WorldRoomsMapper(object):
    """
    Dialogue relations.
    """
    def __init__(self):
        self.model_name = ELEMENT("ROOM").model_name
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)

    def rooms_in_area(self, area_key):
        """
        Get all rooms in an area.

        Args:
            area_key: (string) an area's key.
        """
        # query
        return self.model.objects.filter(area=area_key)


WORLD_ROOMS_MAPPER = WorldRoomsMapper()
