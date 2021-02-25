"""
Query and deal common tables.
"""

from muddery.server.database.dao.base_query import BaseQuery


class EquipmentPositions(BaseQuery):
    """
    Equipment positions data.
    """
    table_name = "equipment_positions"
