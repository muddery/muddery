"""
Query and deal common tables.
"""

from django.apps import apps
from django.conf import settings
from django.db import connections
from django.db.models import Q
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils.exception import MudderyError, ERR


class WorldExitsMapper(object):
    """
    Dialogue relations.
    """
    def __init__(self):
        self.model_name = ELEMENT("EXIT").model_name
        self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)

    def exits_of_rooms(self, rooms):
        """
        Get all exits in rooms

        Args:
            rooms: (list) a list of room's keys.
        """
        return self.model.objects.filter(Q(location__in=rooms) or Q(destination__in=rooms))


WORLD_EXITS_MAPPER = WorldExitsMapper()
