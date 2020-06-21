"""
Query and deal common tables.
"""

from evennia.utils import logger
from django.apps import apps
from django.conf import settings
from muddery.utils import defines
from muddery.worldeditor.dao.common_mapper_base import ObjectsMapper


def get_object_event(object_key):
    """
    Get object's event.
    """
    model = apps.get_model(settings.WORLD_DATA_APP, "event_data")
    return model.objects.filter(trigger_obj=object_key)
