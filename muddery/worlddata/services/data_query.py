"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

import ast
from django.core.exceptions import ObjectDoesNotExist
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.dao import common_mappers as CM
from muddery.worlddata.dao.common_mappers import WORLD_AREAS
from muddery.worlddata.dao.world_rooms_mapper import WORLD_ROOMS_MAPPER
from muddery.worlddata.dao.world_exits_mapper import WORLD_EXITS_MAPPER
from muddery.worlddata.dao import general_query_mapper, model_mapper
from muddery.worlddata.dao.dialogue_sentences_mapper import DIALOGUE_SENTENCES
from muddery.worlddata.dao.object_properties_mapper import OBJECT_PROPERTIES
from muddery.worlddata.dao.event_mapper import get_object_event
from muddery.worlddata.services.general_query import query_fields
from muddery.mappings.typeclass_set import TYPECLASS_SET, TYPECLASS
from muddery.mappings.event_action_set import EVENT_ACTION_SET
from muddery.utils.exception import MudderyError, ERR
from muddery.utils.localized_strings_handler import _


def query_all_typeclasses():
    """
    Query all typeclasses.
    """
    return TYPECLASS_SET.get_all_info()


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


def query_typeclass_properties(typeclass_key):
    """
    Query a typeclass's properties.

    Args:
        typeclass_key: (string) typeclass' key.
    """
    fields = query_fields("properties_dict")
    records = CM.PROPERTIES_DICT.filter(typeclass=typeclass_key)
    rows = []
    for record in records:
        line = [str(record.serializable_value(field["name"])) for field in fields]
        rows.append(line)

    table = {
        "fields": fields,
        "records": rows,
    }
    return table


def query_object_properties(typeclass_key, object_key):
    """
    Query all properties of the given object.

    Args:
        typeclass_key: (string) typeclass' key.
        object_key: (string) object' key.
    """
    # Get fields.
    fields = []
    fields.append({"name": "level",
                   "label": _("Level"),
                   "help_text": _("Properties's level.")})

    properties_info = TYPECLASS(typeclass_key).get_properties_info()
    for key, info in properties_info.items():
        if info["mutable"]:
            continue

        fields.append({"name": key,
                       "label": info["name"],
                       "help_text": info["desc"]})

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
    records = OBJECT_PROPERTIES.get_properties_all_levels(object_key)
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
    table_name = TYPECLASS("OBJECT").model_name
    record = general_query_mapper.get_record_by_key(table_name, object_key)
    obj_typeclass = record.typeclass

    properties_info = TYPECLASS(obj_typeclass).get_properties_info()

    # Get properties.
    data = {}
    records = OBJECT_PROPERTIES.get_properties(object_key, level)
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


def query_event_triggers(typeclass_key):
    """
    Query all event triggers of the given typeclass.

    Args:
        typeclass_key: (string) the object's typeclass_key.
    """
    return TYPECLASS_SET.get_trigger_types(typeclass_key)


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


def query_dialogue_sentences(dialogue_key):
    """
    Query a dialogue's sentences.

    Args:
        dialogue_key: (string) dialogue's key
    """
    fields = query_fields(DIALOGUE_SENTENCES.model_name)
    records = DIALOGUE_SENTENCES.filter(dialogue_key)
    rows = []
    for record in records:
        line = [str(record.serializable_value(field["name"])) for field in fields]
        rows.append(line)

    table = {
        "fields": fields,
        "records": rows,
    }
    return table


def query_typeclass_table(typeclass_key):
    """
    Query a table of objects of the same typeclass.

    Args:
        typeclass_key: (string) typeclass's key.
    """
    typeclass_cls = TYPECLASS(typeclass_key)
    if not typeclass_cls:
        raise MudderyError(ERR.no_table, "Can not find typeclass %s" % typeclass_key)

    # get all tables' name
    tables = typeclass_cls.get_models()
    if not tables:
        raise MudderyError(ERR.no_table, "Can not get tables of %s" % typeclass_key)

    # get all tables' fields
    # add the first table
    table_fields = query_fields(tables[0])
    fields = [field for field in table_fields if field["name"] != "id"]

    # add other tables
    for table in tables[1:]:
        table_fields = query_fields(table)
        fields.extend([field for field in table_fields if field["name"] != "id" and field["name"] != "key"])

    # get all tables' data
    records = general_query_mapper.get_all_from_tables(tables)

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
        info = {
            "key": record["key"],
            "typeclass": record["typeclass"],
            "name": record["name"],
            "location": record["location"],
            "position": ast.literal_eval(record["position"]),
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
