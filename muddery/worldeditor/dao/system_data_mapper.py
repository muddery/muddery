"""
Query and deal common tables.
"""

from muddery.server.utils.singleton import Singleton
from muddery.worldeditor.dao.common_mapper_base import CommonMapper


class SystemDataMapper(CommonMapper, Singleton):
    """
    The world editor system's data.
    """
    def __init__(self):
        super(SystemDataMapper, self).__init__("system_data")

        if self.count({}) == 0:
            self.add({})

    def get_object_index(self):
        """
        Increase the object index and get the new value.
        """
        record = self.get({}, for_update=True)
        index = record.object_index
        self.update_or_add({}, {
            "object_index": index,
        })

        return index
