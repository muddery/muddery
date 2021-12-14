"""
Query and deal common tables.
"""

from sqlalchemy import select, or_
from muddery.server.utils.singleton import Singleton
from muddery.worldeditor.dao.common_mapper_base import CommonMapper
from muddery.server.mappings.element_set import ELEMENT


class WorldExitsMapper(CommonMapper, Singleton):
    """
    Dialogue relations.
    """
    def __init__(self):
        super(WorldExitsMapper, self).__init__(ELEMENT("EXIT").model_name)

    def exits_of_rooms(self, rooms):
        """
        Get all exits in rooms

        Args:
            rooms: (list) a list of room's keys.
        """
        stmt = select(self.model)
        stmt = stmt.where(or_(self.model.location.in_(rooms), self.model.destination.in_(rooms)))

        result = self.session.execute(stmt)
        return result.scalars().all()
