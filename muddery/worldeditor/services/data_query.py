"""
Battle commands. They only can be used when a character is in a combat.
"""

import ast
from django.conf import settings
from django.db import connections
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.worldeditor.dao import common_mappers as CM
from muddery.worldeditor.dao.common_mappers import WORLD_AREAS
from muddery.worldeditor.dao.world_rooms_mapper import WORLD_ROOMS_MAPPER
from muddery.worldeditor.dao.world_exits_mapper import WORLD_EXITS_MAPPER
from muddery.worldeditor.dao.general_query_mapper import get_record_by_key, get_record, get_all_from_tables, filter_records, get_all_records
from muddery.worldeditor.dao.element_properties_mapper import ELEMENT_PROPERTIES
from muddery.worldeditor.dao.event_mapper import get_object_event
from muddery.worldeditor.services.general_query import query_fields
from muddery.server.mappings.element_set import ELEMENT_SET, ELEMENT
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.server.utils.defines import EventType
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.utils.localized_strings_handler import _


def query_all_elements():
    """
    Query all elements.
    """
    return ELEMENT_SET.get_all_info()


def query_areas():
    """
    Query all areas and rooms.
    """
    records = CM.WORLD_AREAS.all_with_base()
    areas = {r["key"]: {"name": r["name"] + "(" + r["key"] + ")", "rooms": []} for r in records}

    rooms = CM.WORLD_ROOMS.all_with_base()
    for record in rooms:
        key = record["location"]
        choice = (record["key"], record["name"] + " (" + record["key"] + ")")
        if key in areas:
            areas[key]["rooms"].append(choice)
        elif key:
            areas[key] = {"name": key, "rooms": [choice]}
    return areas


def query_element_properties(element_type):
    """
    Query an element's custom properties.

    Args:
        element_type: (string) the element' type
    """
    table_name = "properties_dict"
    fields = query_fields(table_name)
    records = filter_records(table_name, element_type=element_type)
    rows = []
    for record in records:
        line = [str(record.serializable_value(field["name"])) for field in fields]
        rows.append(line)

    table = {
        "fields": fields,
        "records": rows,
    }
    return table


def query_object_properties(element_type, object_key):
    """
    Query all properties of the given object.

    Args:
        element_type: (string) the object's element type.
        object_key: (string) object' key.
    """
    # Get fields.
    fields = []
    fields.append({
        "name": "level",
        "label": _("Level"),
        "help_text": _("Properties's level.")
    })

    properties_info = ELEMENT(element_type).get_properties_info()
    for key, info in properties_info.items():
        if info["mutable"]:
            continue

        fields.append({
            "name": key,
            "label": info["name"],
            "help_text": info["desc"]
        })

    if len(fields) == 1:
        # No custom properties.
        table = {
            "fields": [],
            "records": [],
        }
        return table

    # Get rows.
    levels = []
    data = {}
    records = ELEMENT_PROPERTIES.get_properties_all_levels(object_key)
    for record in records:
        if record.level not in levels:
            levels.append(record.level)
            data[record.level] = {"level": record.level}
        data[record.level][record.property] = record.value

    rows = []
    for level in levels:
        line = [data[level].get(field["name"], "") for field in fields]
        rows.append(line)

    table = {
        "fields": fields,
        "records": rows,
    }

    return table


def query_object_level_properties(object_key, level):
    """
    Query properties of a level of the given object.

    Args:
        object_key: (string) object' key.
        level: (number) object's level.
    """
    # Get fields.
    fields = []

    # Object's key.
    fields.append({
        "name": "key",
        "label": _("Key"),
        "disabled": True,
        "help_text": "",
        "type": "TextInput",
        "value": object_key
    })

    # Object's level.
    fields.append({
        "name": "level",
        "label": _("Level"),
        "disabled": False,
        "help_text": "",
        "type": "NumberInput",
        "value": level
    })

    # Get typeclass from the object's record
    table_name = ELEMENT("OBJECT").model_name
    record = get_record_by_key(table_name, object_key)
    obj_typeclass = record.typeclass

    properties_info = ELEMENT(obj_typeclass).get_properties_info()

    # Get properties.
    data = {}
    records = ELEMENT_PROPERTIES.get_properties(object_key, level)
    for record in records:
        data[record.property] = record.value

    # Set fields.
    for key, info in properties_info.items():
        if info["mutable"]:
            continue

        field = {
            "name": key,
            "label": info["name"],
            "disabled": False,
            "help_text": info["desc"],
            "type": "TextInput",
            "value": data.get(key, "")
        }

        fields.append(field)

    return fields


def query_object_event_triggers(typeclass_key):
    """
    Query all event triggers of the given typeclass.

    Args:
        typeclass_key: (string) the object's typeclass_key.
    """
    try:
        return ELEMENT(typeclass_key).get_event_trigger_types()
    except Exception as e:
        return []


def query_dialogue_event_triggers():
    """
    Query all event triggers of dialogues.
    """
    return [EventType.EVENT_TRIGGER_DIALOGUE]


def query_object_events(object_key):
    """
    Query all events of the given object.

    Args:
        object_key: (string) object' key.
    """
    fields = query_fields("event_data")
    records = get_object_event(object_key)
    rows = []
    for record in records:
        line = [str(record.serializable_value(field["name"])) for field in fields]
        rows.append(line)

    table = {
        "fields": fields,
        "records": rows,
    }

    return table


def get_event_data_table(self, event_key):
    """
    Query all actions of an event.

    Args:
        event_key: (string)event's key.
    """
    if not self.model_name:
        return

    fields = query_fields(self.model_name)
    rows = []

    record = get_record(self.model_name, event_key=event_key)
    line = [str(record.serializable_value(field["name"])) for field in fields]
    rows.append(line)

    table = {
        "table": self.model_name,
        "fields": fields,
        "records": rows,
    }
    return table

def query_event_action_data(action_type, event_key):
    """
    Query an event action's data.

    Args:
        action_type: (string) action's type
        event_key: (string) event's key
    """
    # Get action's data.
    action = EVENT_ACTION_SET.get(action_type)
    if not action:
        raise MudderyError(ERR.no_table, "Can not find action: %s" % action_type)

    record = None
    try:
        record = action.get_event_data_table(event_key)
    except ObjectDoesNotExist:
        pass

    return record


def query_element_table(element_type):
    """
    Query a table of objects of the same typeclass.

    Args:
        element_type: (string) element's type
    """
    element_class = ELEMENT(element_type)
    if not element_class:
        raise MudderyError(ERR.no_table, "Can not find the element %s" % element_type)

    # get all tables' name
    tables = element_class.get_models()
    print("tables: %s" % tables)
    if not tables:
        raise MudderyError(ERR.no_table, "Can not get tables of %s" % element_type)

    # get all tables' fields
    # add the first table
    table_fields = query_fields(tables[0])
    print("table_fields: %s" % table_fields)
    fields = [field for field in table_fields if field["name"] != "id"]

    if len(tables) == 1:
        records = get_all_records(tables[0])
        rows = []
        for record in records:
            line = [str(record.serializable_value(field["name"])) for field in fields]
            rows.append(line)
    else:
        # add other tables
        for table in tables[1:]:
            table_fields = query_fields(table)
            fields.extend([field for field in table_fields if field["name"] != "id" and field["name"] != "key"])

        # get all tables' data
        records = get_all_from_tables(tables)
        rows = []
        for record in records:
            line = [str(record[field["name"]]) for field in fields]
            rows.append(line)

    table = {
        "fields": fields,
        "records": rows,
    }
    return table


def query_map(area_key):
    """
    Query the map of an area.

    Args:
        area_key: (string) area's key.
    """
    try:
        area_record = WORLD_AREAS.get_by_key_with_base(area_key)
    except ObjectDoesNotExist:
        raise MudderyError(ERR.no_data, "Can not find map: %s" % area_key)
    area_info = area_record

    room_records = WORLD_ROOMS_MAPPER.rooms_in_area(area_key)
    room_info = []
    room_keys = []
    for record in room_records:
        room_keys.append(record["key"])

        try:
            position = ast.literal_eval(record["position"])
        except SyntaxError as e:
            logger.log_errmsg("Parse map %s's position error: %s" % (record["key"], e))
            position = ()

        info = {
            "key": record["key"],
            "typeclass": record["typeclass"],
            "name": record["name"],
            "location": record["location"],
            "position": position,
            "icon": record["icon"]
        }
        room_info.append(info)

    exit_records = WORLD_EXITS_MAPPER.exits_of_rooms(room_keys)
    exit_info = []
    for record in exit_records:
        info = {
            "key": record["key"],
            "typeclass": record["typeclass"],
            "location": record["location"],
            "destination": record["destination"]
        }
        exit_info.append(info)

    data = {
        "area": area_info,
        "rooms": room_info,
        "exits": exit_info
    }

    return data


def query_dialogues_table():
    """
    Query dialogues.
    """
    cursor = connections[settings.WORLD_DATA_APP].cursor()
    query = "SELECT T1.*, T2.event event, T5.name npc_name, T5.npc npc_key " \
                "FROM (worlddata_dialogues T1 LEFT JOIN " \
                    "(SELECT MIN(T6.key) event, T6.trigger_obj FROM worlddata_event_data T6 " \
                         "WHERE T6.trigger_type='EVENT_TRIGGER_DIALOGUE' GROUP BY trigger_obj) T2 " \
                    "ON T1.key=T2.trigger_obj) " \
                "LEFT JOIN (SELECT T3.npc, T3.dialogue, T4.name FROM worlddata_npc_dialogues T3 " \
                    "JOIN worlddata_objects T4 ON T3.npc=T4.key) T5 " \
                "ON T1.key=T5.dialogue"
    cursor.execute(query)

    fields = query_fields("dialogues")
    # add event and npc fields
    fields.append({
        "default": "",
        "editable": False,
        "help_text": _("Has event.", "help_text"),
        "label": _("event", "field"),
        "name": "event",
        "type": "BooleanField",
    })

    fields.append({
        "default": "",
        "editable": False,
        "help_text": _("Dialogue's NPC.", "help_text"),
        "label": _("NPC", "field"),
        "name": "npc",
        "type": "CharField",
    })

    columns = [col[0] for col in cursor.description]
    key_column = columns.index("key")

    # get records
    rows = []
    record = cursor.fetchone()
    while record is not None:
        if len(rows) > 0 and record[key_column] == rows[-1][key_column]:
            rows[-1][-2] += "," + record[-2] + "(" + record[-1] + ")"
        else:
            row = list(record)
            if not row[-3]:
                row[-3] = ""
            else:
                row[-3] = True

            if not row[-2]:
                row[-2] = ""
            if row[-1]:
                row[-2] += "(" + row[-1] + ")"

            rows.append(row)
        record = cursor.fetchone()

    table = {
        "fields": fields,
        "records": rows,
    }

    return table
