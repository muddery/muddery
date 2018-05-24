"""
Query and deal common tables.
"""

from __future__ import print_function

from evennia.utils import logger
from django.db import transaction
from django.apps import apps
from django.conf import settings
from muddery.utils import defines


def get_object_event(object_key):
    """
    Get object's event.
    """
    model = apps.get_model(settings.WORLD_DATA_APP, "event_data")
    return model.objects.filter(trigger_obj=object_key)


def get_event_additional_data(event_type, event_key):
    """
    Get event's data.
    """
    data = {}
    model_name = ""
    if event_type == defines.EVENT_ATTACK:
        model_name = "event_attacks"
    elif event_type == defines.EVENT_DIALOGUE:
        model_name = "event_dialogues"

    if model_name:
        model = apps.get_model(settings.WORLD_DATA_APP, model_name)
        records = model_additional.objects.filter(key=event_key)
        if records:
            record = records[0]
            for field in record._meta.fields:
                data[field.name] = record.serializable_value(field.name) 




