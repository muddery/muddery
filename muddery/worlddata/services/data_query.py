"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.worlddata.dao import common_mappers as CM
from muddery.worlddata.dao import general_query_mapper, model_mapper
from muddery.worlddata.dao.dialogue_sentences_mapper import DIALOGUE_SENTENCES
from muddery.worlddata.dao.event_mapper import get_object_event
from muddery.mappings.event_action_set import EVENT_ACTION_SET
from muddery.utils.exception import MudderyError, ERR
from muddery.utils.localized_strings_handler import _


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
    models = model_mapper.get_all_models()
    models_info = [{"key": model.__name__,
                    "name": _(model.__name__, category="models") + "(" + model.__name__ + ")"}
                    for model in models if model._meta.app_label == "worlddata"]
    return models_info


def query_areas():
    """
    Query all areas and rooms.
    """
    records = CM.WORLD_AREAS.objects.all()
    areas = {r.key: {"name": r.name + "(" + r.key + ")", "rooms": []} for r in records}

    rooms = CM.WORLD_ROOMS.objects.all()
    for record in rooms:
        key = record.location
        choice = (record.key, record.name + " (" + record.key + ")")
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
