"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.worlddata.dao import common_mapper
from muddery.worlddata.utils import utils
from muddery.utils.exception import MudderyError, ERR
from muddery.utils.localized_strings_handler import _


def query_fields(table_name):
    """
    Query table's data.
    """
    fields = common_mapper.get_all_fields(table_name)
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
    records = common_mapper.get_all_records(table_name)
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
    fields = common_mapper.get_all_fields(table_name)
    record = common_mapper.get_record_by_id(table_name, record_id)
    return [str(record.serializable_value(field.name)) for field in fields]


def query_form(table_name, record_id=None):
    """
    Query table's data.

    Args:
        table_name: (string) data table's name.
        record_id: (string, optional) record's id. If it is empty, query an empty form.
    """
    form_class = common_mapper.get_form(table_name)
    if not form_class:
        raise MudderyError(ERR.no_table, "Can not find table: %s" % table_name)

    form = None
    record = None
    if record_id:
        try:
            # Query record's data.
            record = common_mapper.get_record_by_id(table_name, record_id)
            form = form_class(instance=record)
        except Exception, e:
            form = None

    if not form:
        # Get empty data.
        form = form_class()

    data = []
    for key, field in form.fields.items():
        info = {
            "name": key,
            "label": field.label,
            "disabled": field.disabled,
            "help_text": field.help_text,
            "type": field.widget.__class__.__name__,
        }

        if record:
            info["value"] = str(record.serializable_value(key))

        if info["type"] == "Select":
            info["choices"] = field.choices

        data.append(info)

    return data


def save_form(values, table_name, record_id=None):
    """
    Save data to a record.
    
    Args:
        values: (dict) values to save.
        table_name: (string) data table's name.
        record_id: (string, optional) record's id. If it is empty, add a new record.
    """
    form_class = common_mapper.get_form(table_name)
    if not form_class:
        raise MudderyError(ERR.no_table, "Can not find table: %s" % table_name)

    form = None
    record = None
    if record_id:
        try:
            # Query record's data.
            record = common_mapper.get_record_by_id(table_name, record_id)
            form = form_class(values, instance=record)
        except Exception, e:
            form = None

    if not form:
        # Get empty data.
        form = form_class(values)

    # Save data
    if form.is_valid():
        instance = form.save()
        return instance.pk
    else:
        raise MudderyError(ERR.invalid_form, "Invalid form.", data=form.errors)


def delete_record(table_name, record_id):
    """
    Delete a record of a table.
    """
    common_mapper.delete_record_by_id(table_name, record_id)


def query_tables():
    """
    Query all tables' names.
    """
    models = common_mapper.query_all_models()
    models_info = [{"key": model.__name__,
                    "name": _(model.__name__, category="models") + "(" + model.__name__ + ")"}
                    for model in models if model._meta.app_label == "worlddata"]
    return models_info

