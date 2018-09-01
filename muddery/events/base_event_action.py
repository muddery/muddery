"""
Event action's base class.
"""

from muddery.worlddata.services.data_query import query_fields
from muddery.worlddata.dao import general_query_mapper


class BaseEventAction(object):
    """
    Event action's base class.
    """
    # action's key
    key = ""

    # action's readable name
    name = ""

    # action's additional data table
    model_name = ""

    def func(self, event, character):
        """
        Event action's function.
        """
        pass

    def query_event_data_table(self, event_key):
        """
        Query all actions of an event.

        Args:
            event_key: (string)event's key.
        """
        if not self.model_name:
            return

        fields = query_fields(self.model_name)
        records = general_query_mapper.filter_records(self.model_name, event_key=event_key)
        rows = []
        for record in records:
            line = [str(record.serializable_value(field["name"])) for field in fields]
            rows.append(line)

        table = {
            "fields": fields,
            "records": rows,
        }
        return table
