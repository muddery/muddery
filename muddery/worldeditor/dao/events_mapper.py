"""
Query and deal common tables.
"""

from muddery.common.utils.singleton import Singleton
from muddery.worldeditor.dao.common_mapper_base import CommonMapper


class EventsMapper(CommonMapper, Singleton):
    """
    Object's properties.
    """
    def __init__(self):
        super(EventsMapper, self).__init__("event_data")

    def get_element_events(self, element_key):
        """
        Get object's event.
        """
        return self.filter({
            "trigger_obj": element_key
        })
