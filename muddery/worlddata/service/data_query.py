"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.worlddata.dao import common_mapper
from muddery.worlddata.utils import utils


def query_fields(model_name):
    """
    Query table's data.
    """
    fields = common_mapper.get_all_fields(model_name)
    return [{"name": field.get_attname(),
             "label": field.verbose_name,
             "default": field.get_default(),
             "editable": field.editable,
             "help_text": field.help_text,
             "type": field.__class__.__name__} for field in fields]


def query_table(model_name):
    """
    Query table's data.
    """
    fields = query_fields(model_name)
    records = common_mapper.get_all_records(model_name)
    rows = []
    for record in records:
        line = [str(record.serializable_value(field["name"])) for field in fields]
        rows.append(line)

    table ={
        "fields": fields,
        "rows": rows,
    }
    return table


def query_record(model_name, record_id):
    """
    Query a record of a table.
    """
    fields = common_mapper.get_all_fields(model_name)
    record = common_mapper.get_record_by_id(model_name, record_id)
    return [str(record.serializable_value(field.name)) for field in fields]


def query_form(model_name, record_id):
    """
    Query table's data.
    """
    form_class = common_mapper.get_form(model_name)
    if not form_class:
        return []

    form = None
    record = None
    if record_id:
        try:
            # Query record's data.
            record = common_mapper.get_record_by_id(model_name, record_id)
            form = form_class(instance=record)
        except Exception, e:
            form = None

    if not form:
        # Get empty data.
        form = form_class()

    data = [{"name": key,
             "label": field.label,
             "disabled": field.disabled,
             "help_text": field.help_text,
             "value": field.initial,
             "type": field.__class__.__name__} for key, field in form.fields.items()]
