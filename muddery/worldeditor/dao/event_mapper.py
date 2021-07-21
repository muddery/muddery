"""
Query and deal common tables.
"""

from evennia.utils import logger
from django.apps import apps
from django.conf import settings
from muddery.server.utils import defines


def get_element_event(element_key):
    """
    Get object's event.
    """
    model = apps.get_model(settings.WORLD_DATA_APP, "event_data")
    return model.objects.filter(trigger_obj=element_key)
