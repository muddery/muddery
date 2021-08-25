"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery


class EquipmentPositions(BaseQuery):
    """
    Equipment positions data.
    """
    table_name = "equipment_positions"
