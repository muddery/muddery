"""
Query and deal common tables.
"""

from __future__ import print_function

from django.apps import apps
from django.conf import settings
from django.db import connections
from muddery.mappings.typeclass_set import TYPECLASS
from muddery.utils.exception import MudderyError, ERR


class WorldRoomsMapper(object):
    """
    Dialogue relations.
    """
    def __init__(self):
        self.model_name = TYPECLASS("ROOM").model_name
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects
        self.object_model_name = TYPECLASS("OBJECT").model_name

    def rooms_in_area(self, area_key):
        """
        Get all rooms in an area.

        Args:
            area_key: (string) an area's key.
        """
        # Get table's full name
        object_table = settings.WORLD_DATA_APP + "_" + self.object_model_name
        room_table = settings.WORLD_DATA_APP + "_" + self.model_name

        # query
        query = "select * from %(object)s, %(room)s where %(object)s.key=%(room)s.key and %(room)s.location=%%s"\
                    % {"object": object_table, "room": room_table}
        cursor = connections[settings.WORLD_DATA_APP].cursor()
        cursor.execute(query, [area_key])
        columns = [col[0] for col in cursor.description]

        # return records
        record = cursor.fetchone()
        while record is not None:
            yield dict(zip(columns, record))
            record = cursor.fetchone()


WORLD_ROOMS_MAPPER = WorldRoomsMapper()
