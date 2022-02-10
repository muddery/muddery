"""
Query and deal common tables.
"""

from muddery.common.utils.singleton import Singleton
from muddery.worldeditor.dao.common_mapper_base import CommonMapper
from muddery.server.mappings.element_set import ELEMENT


class WorldRoomsMapper(CommonMapper, Singleton):
    """
    Dialogue relations.
    """
    def __init__(self):
        super(WorldRoomsMapper, self).__init__(ELEMENT("ROOM").model_name)

    def rooms_in_area(self, area_key):
        """
        Get all rooms in an area.

        Args:
            area_key: (string) an area's key.
        """
        return self.filter({
            "area": area_key
        })
