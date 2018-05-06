"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from django.db import transaction
from django.apps import apps
from django.conf import settings
from worlddata.forms import Manager


def get_all_fields(table_name):
    """
    Get all columns informatin.

    Args:
        table_name: (string) db table's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj._meta.fields


def get_all_records(table_name):
    """
    Get a table's all records.

    Args:
        table_name: (string) db table's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj.objects.all()


def get_record_by_id(table_name, record_id):
    """
    Get a table's all records.

    Args:
        table_name: (string) db table's name.
        record_id: (number) record's id.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj.objects.get(id=record_id)


def get_form(table_name):
    """
    Get model's form.

    Args:
        table_name: (string) db table's name.
    """
    return Manager.get_form(table_name)


def delete_record_by_id(table_name, record_id):
    """
    Get a table's all records.

    Args:
        table_name: (string) db table's name.
        record_id: (number) record's id.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    record = model_obj.objects.get(id=record_id)
    record.delete()

