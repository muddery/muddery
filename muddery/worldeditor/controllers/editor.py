"""
Battle commands. They only can be used when a character is in a combat.
"""

import json, traceback
from muddery.worldeditor.services import data_query, data_edit, general_query
from muddery.server.server import Server
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.utils.logger import game_editor_logger as logger
from muddery.worldeditor.utils.response import success_response
from muddery.worldeditor.controllers.base_request_processer import BaseRequestProcesser
from muddery.worldeditor.dao import general_query_mapper
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.server.database.worlddata.worlddata import WorldData


class QueryAllElements(BaseRequestProcesser):
    """
    Query all elements.

    Args:
        None.
    """
    path = "query_all_elements"
    name = ""

    def func(self, args, request):
        data = data_query.query_all_elements()
        return success_response(data)


class QueryFields(BaseRequestProcesser):
    """
    Query all fields of a table.

    Args:
        None.
    """
    path = "query_fields"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        table_name = args["table"]

        data = general_query.query_fields(table_name)
        return success_response(data)


class QueryTable(BaseRequestProcesser):
    """
    Query all records of a table.

    Args:
        None.
    """
    path = "query_table"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        table_name = args["table"]

        data = general_query.query_table(table_name)
        return success_response(data)


class QueryElementTable(BaseRequestProcesser):
    """
    Query a table of objects of the same element type.

    Args:
        element_type: (string) element type.
    """
    path = "query_element_table"
    name = ""

    def func(self, args, request):
        if 'element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_type".')

        element_type = args["element_type"]

        # Query data.
        data = data_query.query_element_table(element_type)
        return success_response(data)


class QueryRecord(BaseRequestProcesser):
    """
    Query a record of a table.

    Args:
        table: (string) table's name.
        record: (string) record's id.
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


class QueryAreas(BaseRequestProcesser):
    """
    Query all available areas.

    Args:
        None.
    """
    path = "query_areas"
    name = ""

    def func(self, args, request):
        data = data_query.query_areas()
        return success_response(data)


class QueryElementTypeProperties(BaseRequestProcesser):
    """
    Query an element's properties.

    Args:
        element: (string) element's type.
    """
    path = "query_element_type_properties"
    name = ""

    def func(self, args, request):
        if 'element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_type".')

        element_type = args["element_type"]

        data = data_query.query_element_type_properties(element_type)
        return success_response(data)


class QueryElementProperties(BaseRequestProcesser):
    """
    Query an object's properties.

    Args:
        element_type: (string) element's type
        element_key: (string) element's key.
    """
    path = "query_element_properties"
    name = ""

    def func(self, args, request):
        if 'element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_type".')

        if 'element_key' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_key".')

        element_type = args["element_type"]
        element_key = args["element_key"]

        data = data_query.query_element_properties(element_type, element_key)
        return success_response(data)


class QueryElementLevelProperties(BaseRequestProcesser):
    """
    Query a level of an object's properties.

    Args:
        element_key: (string) the element's key.
        level: (number) level's number
    """
    path = "query_element_level_properties"
    name = ""

    def func(self, args, request):
        if 'element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_type".')

        if 'element_key' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_key".')

        if 'level' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "level".')

        element_type = args["element_type"]
        element_key = args["element_key"]
        level = args["level"]
        if level == "":
            level = None

        data = data_query.query_element_level_properties(element_type, element_key, level)
        return success_response(data)


class SaveElementLevelProperties(BaseRequestProcesser):
    """
    Save properties of an object.

    Args:
        obj_key: (string) object's key.
        level: (number) level's number.
        values: (dict) values to save.
    """
    path = "save_element_level_properties"
    name = ""

    def func(self, args, request):
        if 'element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_type".')

        if 'element_key' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_key".')

        if 'level' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "level".')

        if 'values' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "values".')

        element_type = args["element_type"]
        element_key = args["element_key"]
        level = args["level"]
        if level == "":
            level = None

        values = args["values"]

        data_edit.save_element_level_properties(element_type, element_key, level, values)
        return success_response("success")


class DeleteElementLevelProperties(BaseRequestProcesser):
    """
    Query a level of an object's properties.

    Args:
        obj_key: (string) object's key.
        level: (number) level's number
    """
    path = "delete_element_level_properties"
    name = ""

    def func(self, args, request):
        if 'element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_type".')

        if 'element_key' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_key".')

        if 'level' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "level".')

        element_type = args["element_type"]
        element_key = args["element_key"]
        level = args["level"]
        if level == "":
            level = None

        data_edit.delete_element_level_properties(element_type, element_key, level)
        data = {"level": level}
        return success_response(data)


class QueryElementEventTriggers(BaseRequestProcesser):
    """
    Query all event triggers of the given element type.

    Args:
        element_type: (string) the element type.
    """
    path = "query_element_event_triggers"
    name = ""

    def func(self, args, request):
        if 'element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_type".')

        element_type = args["element_type"]

        data = data_query.query_element_event_triggers(element_type)
        return success_response(data)


class QueryDialogueEventTriggers(BaseRequestProcesser):
    """
    Query all event triggers of dialogues.
    """
    path = "query_dialogue_event_triggers"
    name = ""

    def func(self, args, request):
        data = data_query.query_dialogue_event_triggers()
        return success_response(data)


class QueryElementEvents(BaseRequestProcesser):
    """
    Query all events of the given element.

    Args:
        element_key: (string) the element's key.
    """
    path = "query_element_events"
    name = ""

    def func(self, args, request):
        if 'element_key' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_key".')

        element_key = args["element_key"]

        data = data_query.query_element_events(element_key)
        return success_response(data)


class QueryEventActionData(BaseRequestProcesser):
    """
    Query an event action's data.

    Args:
        action: (string) action's type
        event: (string) event's key
    """
    path = "query_event_action_data"
    name = ""

    def func(self, args, request):
        if 'action' not in args or 'event' not in args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        action_type = args["action"]
        event_key = args["event"]

        data = data_query.query_event_action_data(action_type, event_key)
        return success_response(data)


class QueryEventActionForm(BaseRequestProcesser):
    """
    Query the form of the event action.

    Args:
        action: (string) action's type
        event: (string) event's key
    """
    path = "query_event_action_forms"
    name = ""

    def func(self, args, request):
        if 'action' not in args or 'event' not in args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        action_type = args["action"]
        event_key = args["event"]

        data = data_edit.query_event_action_forms(action_type, event_key)
        return success_response(data)


class QueryForm(BaseRequestProcesser):
    """
    Query a form of a record of a table.

    Args:
        table: (string) table's name
        record: (string, optional) record's id. If it is empty, get a new record.
    """
    path = "query_form"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        table_name = args["table"]
        record = args.get('record', None)

        data = data_edit.query_form(table_name, {"id": record})
        return success_response(data)


class QueryFormFirstRecord(BaseRequestProcesser):
    """
    Query a form of the first record of a table.

    Args:
        table: (string) table's name
    """
    path = "query_form_first_record"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        table_name = args["table"]

        try:
            record = general_query_mapper.get_the_first_record(table_name)
            if record:
                record_id = record.id
            else:
                record_id = None
        except Exception as e:
            raise MudderyError(ERR.invalid_form, "Wrong table: %s." % table_name)

        data = data_edit.query_form(table_name, {"id": record_id})
        return success_response(data)


class SaveForm(BaseRequestProcesser):
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
            raise MudderyError(ERR.missing_args, 'Missing the argument: "values".')

        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        values = args["values"]
        table_name = args["table"]
        record_id = args.get('record', None)

        record_id = data_edit.save_form(values, table_name, record_id)
        data = data_edit.query_form(table_name, {"id": record_id})
        return success_response(data)


class SaveEventActionForm(BaseRequestProcesser):
    """
    Save an action's form.

    Args:
        action: (string) action's type.
        event: (string) event's key.
        values: (list) a list of action's values.
    """
    path = "save_event_action_forms"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'action' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "action".')

        if 'event' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "event".')

        if 'values' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "values".')

        action_type = args["action"]
        event_key = args["event"]
        values = args["values"]

        # Get action's data.
        action = EVENT_ACTION_SET.get(action_type)
        if not action:
            raise MudderyError(ERR.no_table, "Can not find action: %s" % action_type)

        table_name = action.model_name

        # Remove old records.
        data_edit.delete_records(table_name, {"event_key": event_key})

        # Add new data.
        for value in values:
            data_edit.save_form(value, table_name)

        return success_response("success")


class QueryObjectForm(BaseRequestProcesser):
    """
    Query a record of an object which may include several tables.

    Args:
        base_element_type: (string) the base type of the object
        obj_element_type: (string, optional) object's element type
        element_key: (string, optional) element's key. If it is empty, get a new object.
    """
    path = "query_element_form"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'base_element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "base_element_type".')

        base_element_type = args["base_element_type"]
        obj_element_type = args.get('obj_element_type', None)
        element_key = args.get('element_key', None)

        data = data_edit.query_element_form(base_element_type, obj_element_type, element_key)
        return success_response(data)


class QueryMap(BaseRequestProcesser):
    """
    Query the map of an area

    Args:
        area: (string) area's key
    """
    path = "query_map"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'area' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "area".')

        area_key = args["area"]

        data = data_query.query_map(area_key)
        return success_response(data)


class SaveElementForm(BaseRequestProcesser):
    """
    Save a form.

    Args:
        tables: (list) a list of table data.
               [{
                 "table": (string) table's name.
                 "values": (string, optional) record's value.
                }]
        base_element_type: (string) object's base type
        obj_element_type: (string) object's element type
        obj_key: (string) object's key. If it is empty or different from the current object's key, get a new object.
    """
    path = "save_element_form"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'tables' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "tables".')

        if 'base_element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "base_element_type".')

        if 'obj_element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "obj_element_type".')

        if 'obj_key' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "obj_key".')

        tables = args["tables"]
        base_element_type = args["base_element_type"]
        obj_element_type = args["obj_element_type"]
        element_key = args["obj_key"]

        new_key = data_edit.save_element_form(tables, obj_element_type, element_key)
        if element_key != new_key:
            data_edit.update_element_key(obj_element_type, element_key, new_key)

        return success_response(new_key)


class AddArea(BaseRequestProcesser):
    """
    Save a new area.

    Args:
        element_type: (string) the area's element type.
        width: (number, optional) the area's width.
        height: (number, optional) the area's height.
    """
    path = "add_area"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_type".')

        element_type = args["element_type"]
        width = args.get("width", 0)
        height = args.get("height", 0)

        forms = data_edit.query_element_form(element_type, element_type, None)
        new_area = []
        for form in forms:
            values = {field["name"]: field["value"] for field in form["fields"] if "value" in field}
            values["width"] = width
            values["height"] = height

            new_area.append({
                "table": form["table"],
                "values": values
            })

        obj_key = data_edit.save_element_form(new_area, element_type, "")
        data = {
            "key": obj_key,
            "width": width,
            "height": height,
        }
        return success_response(data)


class AddRoom(BaseRequestProcesser):
    """
    Save a new room.

    Args:
        element_type: (string) room's element type.
        area: (string) room's area.
        position: (string) room's position string.
    """
    path = "add_room"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_type".')

        if 'area' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "area".')

        element_type = args["element_type"]
        area = args["area"]
        position = args.get("position", None)
        if position:
            position = json.dumps(position)

        forms = data_edit.query_element_form(element_type, element_type, None)
        new_room = []
        for form in forms:
            values = {field["name"]: field["value"] for field in form["fields"] if "value" in field}
            values["area"] = area
            values["position"] = position

            new_room.append({
                "table": form["table"],
                "values": values
            })

        obj_key = data_edit.save_element_form(new_room, element_type, "")
        data = {"key": obj_key}
        return success_response(data)


class DeleteElements(BaseRequestProcesser):
    """
    Delete a list of objects

    Args:
        objects: (list) a list of exit keys.
    """
    path = "delete_elements"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if "elements" not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "elements".')

        elements = args["elements"]

        for element_key in elements:
            data_edit.delete_element(element_key)

        return success_response("success")


class AddExit(BaseRequestProcesser):
    """
    Save a new exit.

    Args:
        element_type: (string) the exit's element type.
        location: (string) exit's location.
        destination: (string) exit's destination.
    """
    path = "add_exit"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_type".')

        if 'location' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "location".')

        if 'destination' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "destination".')

        element_type = args["element_type"]
        location = args["location"]
        destination = args["destination"]

        forms = data_edit.query_element_form(element_type, element_type, None)
        new_exit = []
        for form in forms:
            values = {field["name"]: field["value"] for field in form["fields"] if "value" in field}
            values["location"] = location
            values["destination"] = destination

            new_exit.append({
                "table": form["table"],
                "values": values
            })

        obj_key = data_edit.save_element_form(new_exit, element_type, "")
        data = {"key": obj_key}
        return success_response(data)


class SaveMap(BaseRequestProcesser):
    """
    Save a map.

    Args:
        area: (dict) area's data
              {
                   "key": (string) area's key
                   "background": (string) area's background
                   "width": (number) area's width
                   "height": (number) area's height
              }
        rooms: (dict) rooms positions.
                {
                    "key": (string) room's key
                    "position": (list) room's position
                }
    """
    path = "save_map_positions"
    name = ""

    def func(self, args, request):
        if not args:
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        if 'area' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "area".')

        if 'rooms' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "rooms".')

        area = args["area"]
        rooms = args["rooms"]

        data = data_edit.save_map_positions(area, rooms)
        return success_response(data)


class DeleteRecord(BaseRequestProcesser):
    """
    Delete a record.

    Args:
        table: (string) table's name.
        record: (string) record's id.
    """
    path = "delete_record"
    name = ""

    def func(self, args, request):
        if 'table' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "table".')

        if 'record' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "record".')

        table_name = args["table"]
        record_id = args["record"]

        data_edit.delete_record(table_name, record_id)
        data = {"record": record_id}
        return success_response(data)


class DeleteElement(BaseRequestProcesser):
    """
    Delete an element.

    Args:
        element_key: (string) element's key.
        base_element_type: (string, optional) object's base type. Delete all records in all tables under this element type.
                        If its empty, get the element type of the object.
    """
    path = "delete_element"
    name = ""

    def func(self, args, request):
        if 'element_key' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "element_key".')

        if 'base_element_type' not in args:
            raise MudderyError(ERR.missing_args, 'Missing the argument: "base_element_type".')

        element_key = args["element_key"]
        base_element_type = args.get("base_element_type", None)

        data_edit.delete_element(element_key, base_element_type)
        data = {"element_key": element_key}

        return success_response(data)


class QueryTables(BaseRequestProcesser):
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


class QueryDialoguesTable(BaseRequestProcesser):
    """
    Query all records of dialogues.

    Args:
        None.
    """
    path = "query_dialogues_table"
    name = ""

    def func(self, args, request):
        data = data_query.query_dialogues_table()
        return success_response(data)


class ApplyChanges(BaseRequestProcesser):
    """
    Query all tables' names.

    Args:
        None.
    """
    path = "apply_changes"
    name = ""

    def func(self, args, request):
        try:
            # reload system data
            # import_syetem_data()

            # reload localized strings
            # LOCALIZED_STRINGS_HANDLER.reload()

            # reload data
            WorldData.reload()

            # restart the server
            Server.world.broadcast("Server restarting ...")

            # TODO: Dose not support yet.
            # SESSIONS.portal_restart_server()
        except Exception as e:
            message = "Can not build the world: %s" % e
            logger.log_trace(message)
            raise MudderyError(ERR.build_world_error, message)

        return success_response("success")
