"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery


class ConditionDesc(BaseQuery):
    """
    Descriptions of different conditions.
    """
    table_name = "condition_desc"
