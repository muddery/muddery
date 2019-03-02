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
from muddery.worlddata.dao.event_mapper import get_object_event
from muddery.worlddata.services.general_query import query_fields
from muddery.mappings.typeclass_set import TYPECLASS
from muddery.mappings.event_action_set import EVENT_ACTION_SET
from muddery.utils.exception import MudderyError, ERR


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

    return action.query_event_data_table(event_key)


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
        area_record = WORLD_AREAS.get(key=area_key)
    except ObjectDoesNotExist:
        raise MudderyError(ERR.no_data, "Can not find map: %s" % area_key)

    area_info = {
        "key": area_record.key,
        "background": area_record.background,
        "width": area_record.width,
        "height": area_record.height
    }

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
