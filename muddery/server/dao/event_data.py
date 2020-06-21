
from muddery.server.dao.worlddata import WorldData


class EventData(object):
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
