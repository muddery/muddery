"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.worlddata.dao import general_mapper
from muddery.worlddata.utils import utils
from muddery.utils.exception import MudderyError, ERR
from muddery.utils.localized_strings_handler import _


def query_fields(table_name):
    """
    Query table's data.
    """
    fields = general_mapper.get_all_fields(table_name)
    return [{"name": field.get_attname(),
             "label": field.verbose_name,
             "default": field.get_default(),
             "editable": field.editable,
             "help_text": field.help_text,
             "type": field.__class__.__name__} for field in fields]


def query_table(table_name):
    """
    Query table's data.
    """
    fields = query_fields(table_name)
    records = general_mapper.get_all_records(table_name)
    rows = []
    for record in records:
        line = [str(record.serializable_value(field["name"])) for field in fields]
        rows.append(line)

    table ={
        "fields": fields,
        "records": rows,
    }
    return table


def query_record(table_name, record_id):
    """
    Query a record of a table.
    """
    fields = general_mapper.get_all_fields(table_name)
    record = general_mapper.get_record_by_id(table_name, record_id)
    return [str(record.serializable_value(field.name)) for field in fields]


def query_tables():
    """
    Query all tables' names.
    """
    models = general_mapper.get_all_models()
    models_info = [{"key": model.__name__,
                    "name": _(model.__name__, category="models") + "(" + model.__name__ + ")"}
                    for model in models if model._meta.app_label == "worlddata"]
    return models_info
