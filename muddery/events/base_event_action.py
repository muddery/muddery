"""
Event action's base class.
"""

from django.apps import apps
from django.conf import settings
from muddery.worlddata.services.general_query import query_fields
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

    # action's data model
    __model__ = None

    @classmethod
    def model(cls):
        """
        Get the action's data model.
        """
        if cls.__model__:
            return cls.__model__

        cls.__model__ = apps.get_model(settings.WORLD_DATA_APP, cls.model_name)
        return cls.__model__

    def func(self, event_key, character, obj):
        """
        Event action's function.

        Args:
            event_key: (string) event's key.
            character: (object) relative character.
            obj: (object) the event object.
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
            "table": self.model_name,
            "fields": fields,
            "records": rows,
        }
        return table
