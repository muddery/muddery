"""
Query and deal common tables.
"""

from __future__ import print_function

from django.apps import apps
from django.conf import settings
from django.db import connections
from muddery.mappings.typeclass_set import TYPECLASS
from muddery.utils.exception import MudderyError, ERR


class WorldExitsMapper(object):
    """
    Dialogue relations.
    """
    def __init__(self):
        self.model_name = TYPECLASS("EXIT").model_name
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
        self.objects = self.model.objects
        self.object_model_name = TYPECLASS("OBJECT").model_name

    def exits_of_rooms(self, rooms):
        """
        Get all exits in rooms

        Args:
            rooms: (list) a list of room's keys.
        """
        query_rooms = ",".join(["'%s'" % room for room in rooms])

        # Get table's full name
        object_table = settings.WORLD_DATA_APP + "_" + self.object_model_name
        exit_table = settings.WORLD_DATA_APP + "_" + self.model_name

        # query
        query = "select * from %(object)s, %(exit)s where %(object)s.key=%(exit)s.key and\
                    (%(exit)s.location in (%(rooms)s) or %(exit)s.destination in (%(rooms)s))"\
                    % {"object": object_table, "exit": exit_table, "rooms": query_rooms}
        cursor = connections[settings.WORLD_DATA_APP].cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]

        # return records
        record = cursor.fetchone()
        while record is not None:
            yield dict(zip(columns, record))
            record = cursor.fetchone()


WORLD_EXITS_MAPPER = WorldExitsMapper()
