"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.worlddata.request_mapping import request_mapping
from muddery.worlddata.service import data_query
from muddery.worlddata.utils import utils
from muddery.utils.exception import MudderyError, ERR


@request_mapping()
def query_fields(args, request):
    """
    Query all fields of a table.
    """
    if not args or ('table' not in args):
        raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

    table_name = args["table"]

    return data_query.query_fields(table_name)


@request_mapping()
def query_table(args, request):
    """
    Query all records of a table.
    """
    if not args or ('table' not in args):
        raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

    table_name = args["table"]

    return data_query.query_table(table_name)


@request_mapping()
def query_record(args, request):
    """
    Query a record of a table.
    """
    if not args or ('table' not in args) or ('record' not in args):
        raise MudderyError(ERR.missing_args, 'Missing arguments.')

    table_name = args["table"]
    record_id = args["record"]

    return data_query.query_record(table_name, record_id)


@request_mapping()
def query_form(args, request):
    """
    Query a form.
    """
    if not args or ('table' not in args):
        raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

    table_name = args["table"]
    record = args.get('record', None)

    return data_query.query_form(table_name, record)


@request_mapping()
def save_form(args, request):
    """
    Save a form.

    args:
        values: (dict) values to save.
        table: (string) table's name.
        record: (string, optional) record's id. If it is empty, add a new record.
    """
    if not args:
        raise MudderyError(ERR.missing_args, 'Missing arguments.')

    if 'values' not in args:
        raise MudderyError(ERR.missing_args, 'Missing argument: "values".')

    if 'table' not in args:
        raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

    values = args["values"]
    table_name = args["table"]
    record_id = args.get('record', None)

    record_id = data_query.save_form(values, table_name, record_id)
    return data_query.query_record(table_name, record_id)


@request_mapping()
def delete_record(args, request):
    """
    Delete a record.

    args:
        table: (string) table's name.
        record: (string) record's id.
    """
    if not args or ('table' not in args) or ('record' not in args):
        raise MudderyError(ERR.missing_args, 'Missing arguments.')

    table_name = args["table"]
    record_id = args["record"]

    data_query.delete_record(table_name, record_id)
    return {"record": record_id}


