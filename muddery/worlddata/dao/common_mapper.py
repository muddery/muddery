"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from django.db import transaction
from django.apps import apps
from django.conf import settings


def get_all_fields(model_name):
    """
    Get all columns informatin.

    Args:
        model_name: (string) db model's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
    fields = model_obj._meta.fields
    return [(field.name, field.verbose_name) for field in fields]


def get_all_records(model_name):
    """
    Get a table's all records.

    Args:
        model_name: (string) db model's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
    fields = model_obj._meta.fields

    # get records
    for record in model_obj.objects.all():
        line = [str(record.serializable_value(field.name)) for field in fields]
        yield line


def get_all_records_lines(model_name):
    """
    Transform a db table to a string table.

    Args:
        model_name: (string) db model's name.
    """
    return [line for line in get_all_records(model_name)]

