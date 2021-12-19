"""
Battle commands. They only can be used when a character is in a combat.
"""

from django.conf import settings
from muddery.worldeditor.dao import general_query_mapper
from muddery.server.database.db_manager import DBManager
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.utils.localized_strings_handler import _


def query_fields(table_name):
    """
    Query table's data.
    """
    fields = general_query_mapper.get_all_fields(table_name)
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
    records = general_query_mapper.get_all_records(table_name)
    rows = []
    for record in records:
        line = [str(record.serializable_value(field["name"])) for field in fields]
        rows.append(line)

    table = {
        "fields": fields,
        "records": rows,
    }
    return table


def query_record(table_name, record_id):
    """
    Query a record of a table.
    """
    fields = general_query_mapper.get_all_fields(table_name)
    record = general_query_mapper.get_record_by_id(table_name, record_id)
    return [str(record.serializable_value(field.name)) for field in fields]


def query_tables():
    """
    Query all tables' names.
    """
    tables = DBManager.inst().get_tables()
    models_info = [{
        "key": table,
        "name": _(table, category="models") + "(" + table + ")"
    } for table in tables]
    return models_info
