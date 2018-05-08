"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

import json
from django.conf import settings
from evennia.utils import logger
from evennia.server.sessionhandler import SESSIONS
from muddery.worlddata.request_mapping import request_mapping
from muddery.worlddata.service import data_query
from muddery.utils.exception import MudderyError, ERR
from muddery.worlddata.utils.response import success_response
from muddery.utils.builder import build_all
from muddery.utils.game_settings import GAME_SETTINGS


@request_mapping
def query_fields(args, request):
    """
    Query all fields of a table.
    """
    if 'table' not in args:
        raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

    table_name = args["table"]

    data = data_query.query_fields(table_name)
    return success_response(data)


@request_mapping
def query_table(args, request):
    """
    Query all records of a table.
    """
    if 'table' not in args:
        raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

    table_name = args["table"]

    data = data_query.query_table(table_name)
    return success_response(data)


@request_mapping
def query_record(args, request):
    """
    Query a record of a table.
    """
    if ('table' not in args) or ('record' not in args):
        raise MudderyError(ERR.missing_args, 'Missing arguments.')

    table_name = args["table"]
    record_id = args["record"]

    data = data_query.query_record(table_name, record_id)
    return success_response(data)


@request_mapping
def query_form(args, request):
    """
    Query a form.
    """
    if 'table' not in args:
        raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

    table_name = args["table"]
    record = args.get('record', None)

    data = data_query.query_form(table_name, record)
    return success_response(data)


@request_mapping
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
    data = data_query.query_record(table_name, record_id)
    return success_response(data)


@request_mapping
def delete_record(args, request):
    """
    Delete a record.

    args:
        table: (string) table's name.
        record: (string) record's id.
    """
    if ('table' not in args) or ('record' not in args):
        raise MudderyError(ERR.missing_args, 'Missing arguments.')

    table_name = args["table"]
    record_id = args["record"]

    data_query.delete_record(table_name, record_id)
    data = {"record": record_id}
    return success_response(data)


@request_mapping
def query_tables(args, request):
    """
    Query all tables' names.

    args: None
    """
    data = data_query.query_tables()
    return success_response(data)


@request_mapping
def apply_changes(args, request):
    """
    Apply changes to the game.

    args: None
    """
    try:
        # reload system data
        #import_syetem_data()

        # reload localized strings
        #LOCALIZED_STRINGS_HANDLER.reload()

        # rebuild the world
        build_all()

        # send client settings
        client_settings = GAME_SETTINGS.get_client_settings()
        text = json.dumps({"settings": client_settings})
        SESSIONS.announce_all(text)

        # restart the server
        SESSIONS.announce_all("Server restarting ...")
        SESSIONS.server.shutdown(mode='reload')
    except Exception, e:
        message = "Can not build the world: %s" % e
        logger.log_tracemsg(message)
        raise MudderyError(ERR.build_world_error, message)

    return success_response("success")

