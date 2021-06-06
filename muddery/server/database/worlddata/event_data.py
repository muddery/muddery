"""
Query and deal common tables.
"""

from muddery.server.database.worlddata.base_query import BaseQuery
from muddery.server.database.worlddata.worlddata import WorldData


class EventData(BaseQuery):
    """
    Object's event data.
    """
    table_name = "event_data"

    @classmethod
    def get_object_event(cls, trigger_type, trigger_obj):
        """
        Get object's event.
        """
        return WorldData.get_table_data(cls.table_name, trigger_type=trigger_type, trigger_obj=trigger_obj)
