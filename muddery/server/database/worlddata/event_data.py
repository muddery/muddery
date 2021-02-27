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
    def get_object_event(cls, object_key):
        """
        Get object's event.
        """
        return WorldData.get_table_data(cls.table_name, trigger_obj=object_key)
