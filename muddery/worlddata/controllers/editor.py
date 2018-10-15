"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

import json
from django.conf import settings
from evennia.utils import logger
from evennia.server.sessionhandler import SESSIONS
from muddery.worlddata.services import data_query, data_edit, general_query
from muddery.utils.exception import MudderyError, ERR
from muddery.worlddata.utils.response import success_response
from muddery.utils.builder import build_all
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.controllers.base_request_processer import BaseRequestProcesser


class query_fields(BaseRequestProcesser):
    """
    Query all fields of a table.

    Args:
        None
    """
    path = "query_fields"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

        table_name = args["table"]

        data = general_query.query_fields(table_name)
        return success_response(data)


class query_table(BaseRequestProcesser):
    """
    Query all records of a table.

    Args:
        None
    """
    path = "query_table"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

        table_name = args["table"]

        data = general_query.query_table(table_name)
        return success_response(data)


class query_record(BaseRequestProcesser):
    """
    Query a record of a table.

    Args:
        table: (string) table's name
        record: (string) record's id
    """
    path = "query_record"
    name = ""

    def func(self, args, request):
        if ('table' not in args) or ('record' not in args):
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        table_name = args["table"]
        record_id = args["record"]

        data = general_query.query_record(table_name, record_id)
        return success_response(data)


class query_areas(BaseRequestProcesser):
    """
    Query all available areas.

    Args:
        None
    """
    path = "query_areas"
    name = ""

    def func(self, args, request):
        data = data_query.query_areas()
        return success_response(data)


class query_object_events(BaseRequestProcesser):
    """
    Query all events of the given object.

    Args:
        object: (string) object's key
    """
    path = "query_object_events"
    name = ""

    def func(self, args, request):
        if ('object' not in args):
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        object_key = args["object"]

        data = data_query.query_object_events(object_key)
        return success_response(data)


class query_event_action_data(BaseRequestProcesser):
    """
    Query an event action's data.

    Args:
        type: (string) action's type
        key: (string) event's key
    """
    path = "query_event_action_data"
    name = ""

    def func(self, args, request):
        if ('type' not in args or 'key' not in args):
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        action_type = args["type"]
        event_key = args["key"]

        data = data_query.query_event_action_data(action_type, event_key)
        return success_response(data)


class query_dialogue_sentences(BaseRequestProcesser):
    """
    Query a dialogue's sentences.

    Args:
        key: (string) dialogue's key
    """
    path = "query_dialogue_sentences"
    name = ""

    def func(self, args, request):
        if ('dialogue' not in args):
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        dialogue_key = args["dialogue"]

        data = data_query.query_dialogue_sentences(dialogue_key)
        return success_response(data)


class query_form(BaseRequestProcesser):
    """
    Query a record of a table.

    Args:
        table: (string) table's name
    """
    path = "query_form"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

        table_name = args["table"]
        record = args.get('record', None)

        data = data_edit.query_form(table_name, record)
        return success_response(data)


class save_form(BaseRequestProcesser):
    """
    Save a form.

    Args:
        values: (dict) values to save.
        table: (string) table's name.
        record: (string, optional) record's id. If it is empty, add a new record.
    """
    path = "save_form"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'values' not in args:
            raise MudderyError(ERR.missing_args, 'Missing argument: "values".')

        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing argument: "table".')

        values = args["values"]
        table_name = args["table"]
        record_id = args.get('record', None)

        record_id = data_edit.save_form(values, table_name, record_id)
        data = general_query.query_record(table_name, record_id)
        return success_response(data)


class delete_record(BaseRequestProcesser):
    """
    Delete a record.

    Args:
        table: (string) table's name.
        record: (string) record's id.
    """
    path = "delete_record"
    name = ""

    def func(self, args, request):
        if ('table' not in args) or ('record' not in args):
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        table_name = args["table"]
        record_id = args["record"]

        data_edit.delete_record(table_name, record_id)
        data = {"record": record_id}
        return success_response(data)


class query_tables(BaseRequestProcesser):
    """
    Query all tables' names.

    Args:
        None
    """
    path = "query_tables"
    name = ""

    def func(self, args, request):
        data = general_query.query_tables()
        return success_response(data)


class apply_changes(BaseRequestProcesser):
    """
    Query all tables' names.

    Args:
        None
    """
    path = "apply_changes"
    name = ""

    def func(self, args, request):
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
