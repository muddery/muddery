"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from django.db import transaction
from django.apps import apps
from django.conf import settings


def to_lines(model_name):
    """
    Transform a db table to string lines.

    Args:
        model_name: (string) db model's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
    fields = model_obj._meta.fields
    yield [field.name for field in fields]

    # get records
    for record in model_obj.objects.all():
        line = [str(record.serializable_value(field.name)) for field in fields]
        yield line


def to_str(model_name):
    """
    Transform a db table to a string table.

    Args:
        model_name: (string) db model's name.
    """
    return [line for line in to_lines(model_name)]

