"""
Battle commands. They only can be used when a character is in a combat.
"""

import ast
from sqlalchemy.sql import text
from muddery.server.utils.logger import logger
from muddery.server.mappings.element_set import ELEMENT_SET, ELEMENT
from muddery.server.utils.defines import EventType
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.utils.localized_strings_handler import _
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.dao.common_mappers import WORLD_AREAS
from muddery.worldeditor.dao.world_rooms_mapper import WorldRoomsMapper
from muddery.worldeditor.dao.world_exits_mapper import WorldExitsMapper
from muddery.worldeditor.dao.element_properties_mapper import ElementPropertiesMapper
from muddery.worldeditor.dao.events_mapper import EventsMapper
from muddery.worldeditor.dao import general_querys
from muddery.worldeditor.database.db_manager import DBManager
from muddery.worldeditor.mappings.form_set import FORM_SET


def query_fields_info(table_name):
    """
    Query table's data.
    """
    field_names = general_querys.get_field_names(table_name)
    form_class = FORM_SET.get(table_name)
    form = form_class()

    fields = []
    for field_name in field_names:
        field = form[field_name]
        info = {
            "name": field.id,
            "label": field.name,
            "default": field.default,
            "disabled": (field.name == "id"),
            "help_text": field.description,
            "type": type(field.widget).__name__,
        }
        fields.append(info)

    return fields


def query_table(table_name):
    """
    Query table's data.
    """
    fields = query_fields_info(table_name)
    records = general_querys.get_all_records(table_name)
    rows = []
    for record in records:
        line = [getattr(record, field["name"]) for field in fields]
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
    fields = query_fields_info(table_name)
    record = general_querys.get_record_by_id(table_name, record_id)
    return [getattr(record, field["name"]) for field in fields]


def query_tables():
    """
    Query all tables' names.
    """
    tables = DBManager.inst().get_tables(SETTINGS.WORLD_DATA_APP)
    models_info = [{
        "key": table,
        "name": _(table, category="models") + "(" + table + ")"
    } for table in tables]
    return models_info


def query_all_elements():
    """
    Query all elements.
    """
    return ELEMENT_SET.get_all_info()


def query_areas():
    """
    Query all areas and rooms.
    """
    area_class = ELEMENT("AREA")
    if not area_class:
        raise MudderyError(ERR.no_table, "Can not find the element AREA")

    room_class = ELEMENT("ROOM")
    if not room_class:
        raise MudderyError(ERR.no_table, "Can not find the element AREA")

    records = general_querys.get_all_records(area_class.model_name)
    areas = {r.key: {"name": r.name + "(" + r.key + ")", "rooms": []} for r in records}

    records = general_querys.get_all_records(room_class.model_name)
    for r in records:
        key = r.area
        choice = (r.key, r.name + " (" + r.key + ")")
        if key in areas:
            areas[key]["rooms"].append(choice)
        elif key:
            areas[key] = {"name": key, "rooms": [choice]}
    return areas


def query_element_type_properties(element_type):
    """
    Query an element's custom properties.

    Args:
        element_type: (string) the element' type
    """
    table_name = "properties_dict"
    fields = query_fields_info(table_name)
    records = general_querys.filter_records(table_name, {
        "element_type": element_type
    })
    rows = []
    for record in records:
        line = [getattr(record, field["name"]) for field in fields]
        rows.append(line)

    table = {
        "fields": fields,
        "records": rows,
    }
    return table


def query_element_properties(element_type, element_key):
    """
    Query all properties of the given element.

    Args:
        element_type: (string) the object's element type.
        element_key: (string) object's element key.
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
    records = ElementPropertiesMapper.inst().get_properties_all_levels(element_type, element_key)
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


def query_element_level_properties(element_type, element_key, level):
    """
    Query properties of a level of the given object.

    Args:
        element_type: (string) the object's type.
        element_key: (string) the element' key.
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
        "value": element_key
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

    properties_info = ELEMENT(element_type).get_properties_info()

    # Get properties.
    data = {}
    records = ElementPropertiesMapper.inst().get_properties(element_type, element_key, level)
    for record in records:
        data[record.property] = record.value

    # Set fields.
    for key, info in properties_info.items():
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


def query_conditional_desc(element_type, element_key):
    """
    Query all properties of the given element.

    Args:
        element_type: (string) the object's element type.
        element_key: (string) object's element key.
    """
    # Get fields.
    table_fields = query_fields_info("conditional_desc")
    fields = [field for field in table_fields if field["name"] != "element" and field["name"] != "key"]
    records = general_querys.filter_records("conditional_desc", {
        "element": element_type,
        "key": element_key,
    })
    rows = []
    for record in records:
        line = [getattr(record, field["name"]) for field in fields]
        rows.append(line)

    table = {
        "fields": fields,
        "records": rows,
    }
    return table


def query_element_event_triggers(element_type):
    """
    Query all event triggers of the given element type.

    Args:
        element_type: (string) the object's element type.
    """
    try:
        return ELEMENT(element_type).get_event_trigger_types()
    except Exception as e:
        return []


def query_dialogue_event_triggers():
    """
    Query all event triggers of dialogues.
    """
    return [EventType.EVENT_TRIGGER_DIALOGUE]


def query_element_events(element_key):
    """
    Query all events of the given element.

    Args:
        element_key: (string) the element' key.
    """
    fields = query_fields_info("event_data")
    records = EventsMapper.inst().get_element_events(element_key)
    rows = []
    for record in records:
        line = [getattr(record, field["name"]) for field in fields]
        rows.append(line)

    table = {
        "fields": fields,
        "records": rows,
    }

    return table


def query_element_table(element_type):
    """
    Query all objects of the same element type.

    Args:
        element_type: (string) element's type
    """
    element_class = ELEMENT(element_type)
    if not element_class:
        raise MudderyError(ERR.no_table, "Can not find the element %s" % element_type)

    # get all tables' name
    tables = element_class.get_models()
    if not tables:
        raise MudderyError(ERR.no_table, "Can not get tables of %s" % element_type)

    # get all tables' fields
    # add the first table
    table_fields = query_fields_info(tables[0])
    fields = [field for field in table_fields if field["name"] != "id"]

    if len(tables) == 1:
        records = general_querys.get_all_records(tables[0])
        rows = []
        for record in records:
            line = [getattr(record, field["name"]) for field in fields]
            rows.append(line)
    else:
        # add other tables
        for table in tables[1:]:
            table_fields = query_fields_info(table)
            fields.extend([field for field in table_fields if field["name"] != "name" and field["name"] != "key"])

        # get all tables' data
        records = general_querys.get_all_from_tables(tables)
        rows = []
        for record in records:
            line = [getattr(record, field["name"]) for field in fields]
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
    area_table_fields = general_querys.get_field_names("world_areas")
    area_records = WORLD_AREAS.get_by_key_with_base(area_key)
    if not area_records:
        raise MudderyError(ERR.no_data, "Can not find map: %s" % area_key)
    area_record = area_records[0]
    area_info = {field: getattr(area_record, field) for field in area_table_fields}

    room_records = WorldRoomsMapper.inst().rooms_in_area(area_key)
    room_info = []
    room_keys = []
    for record in room_records:
        room_keys.append(record.key)

        try:
            position = ast.literal_eval(record.position)
        except SyntaxError as e:
            logger.log_err("Parse map %s's position error: %s" % (record["key"], e))
            position = ()

        info = {
            "key": record.key,
            "element_type": record.element_type,
            "name": record.name,
            "area": record.area,
            "position": position,
            "icon": record.icon
        }
        room_info.append(info)

    exit_records = WorldExitsMapper.inst().exits_of_rooms(room_keys)
    exit_info = []
    for record in exit_records:
        info = {
            "key": record.key,
            "element_type": record.element_type,
            "location": record.location,
            "destination": record.destination
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
    session_name = SETTINGS.WORLD_DATA_APP
    session = DBManager.inst().get_session(session_name)
    stmt = text("SELECT T1.*, T2.event event, T5.name npc_name, T5.npc npc_key " \
                "FROM (dialogues T1 LEFT JOIN " \
                    "(SELECT MIN(T6.key) event, T6.trigger_obj FROM event_data T6 " \
                         "WHERE T6.trigger_type='EVENT_TRIGGER_DIALOGUE' GROUP BY trigger_obj) T2 " \
                    "ON T1.key=T2.trigger_obj) " \
                "LEFT JOIN (SELECT T3.npc, T3.dialogue, T4.name FROM npc_dialogues T3 " \
                    "JOIN characters T4 ON T3.npc=T4.key) T5 " \
                "ON T1.key=T5.dialogue")

    result = session.execute(stmt)

    fields = query_fields_info("dialogues")
    # add event and npc fields
    fields.append({
        "default": "",
        "disabled": True,
        "help_text": _("Has event.", "help_text"),
        "label": _("event", "field"),
        "name": "event",
        "type": "BooleanField",
    })

    fields.append({
        "default": "",
        "disabled": True,
        "help_text": _("Dialogue's NPC.", "help_text"),
        "label": _("NPC", "field"),
        "name": "npc",
        "type": "CharField",
    })

    columns = [col[0] for col in result.cursor.description]
    key_column = columns.index("key")

    # get records
    rows = []
    record = result.fetchone()
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
        record = result.fetchone()

    table = {
        "fields": fields,
        "records": rows,
    }

    return table
