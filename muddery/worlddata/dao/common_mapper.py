"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from django.db import transaction
from django.apps import apps
from django.conf import settings
from worlddata.forms import Manager


def get_all_fields(model_name):
    """
    Get all columns informatin.

    Args:
        model_name: (string) db model's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
    return model_obj._meta.fields


def get_all_records(model_name):
    """
    Get a table's all records.

    Args:
        model_name: (string) db model's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
    return model_obj.objects.all()


def get_record_by_id(model_name, record_id):
    """
    Get a table's all records.

    Args:
        model_name: (string) db model's name.
        record_id: (number) record's id.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
    return model_obj.objects.get(id=record_id)


def get_form(model_name):
    """
    Get model's form.

    Args:
        model_name: (string) db model's name.
    """
    return Manager.get_form(model_name)



