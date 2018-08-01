"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError, ERR
from muddery.utils.localized_strings_handler import _
from muddery.worlddata.dao import general_query_mapper
from muddery.worlddata.dao import common_mappers as CM
from muddery.worlddata.dao.event_mapper import get_object_event
from muddery.mappings.form_set import FORM_SET
from muddery.mappings.typeclass_set import TYPECLASS_SET
from muddery.worlddata.forms.default_forms import ObjectsForm
from muddery.worlddata.forms.location_field import LocationField
from muddery.worlddata.forms.image_field import ImageField


def query_form(table_name, record_id=None):
    """
    Query table's data.

    Args:
        table_name: (string) data table's name.
        record_id: (string, optional) record's id. If it is empty, query an empty form.
    """
    form_class = FORM_SET.get(table_name)
    if not form_class:
        raise MudderyError(ERR.no_table, "Can not find table: %s" % table_name)

    form = None
    record = None
    if record_id:
        try:
            # Query record's data.
            record = general_query_mapper.get_record_by_id(table_name, record_id)
            form = form_class(instance=record)
        except Exception, e:
            form = None

    if not form:
        # Get empty data.
        form = form_class()

    fields = []
    fields.append({
        "name": "id",
        "label": "",
        "disabled": True,
        "help_text": "",
        "type": "Hidden",
        "value": record_id if record_id else "",
    })

    has_location = False
    for key, field in form.fields.items():
        info = {
            "name": key,
            "label": field.label,
            "disabled": field.disabled,
            "help_text": field.help_text,
            "type": field.widget.__class__.__name__,
        }

        if record:
            info["value"] = str(record.serializable_value(key))

        if info["type"] == "Select":
            info["choices"] = field.choices

        if isinstance(field, LocationField):
            info["type"] = "Location"
            has_location = True
        elif isinstance(field, ImageField):
            info["type"] = "Image"
            info["image_type"] = field.get_type()

        fields.append(info)

    data = {
        "fields": fields,
    }

    if has_location:
        data["areas"] = query_areas()

    if isinstance(form, ObjectsForm):
        data["events"] = []
        if record:
            events = get_object_event(record.key)
            data["events"] = [{"key": e.key,
                               "trigger_type": e.trigger_type,
                               "event_type": e.type,
                               "one_time": e.one_time,
                               "odds": e.odds,
                               "condition": e.condition,
                               } for e in events]

    return data


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


def save_form(values, table_name, record_id=None):
    """
    Save data to a record.
    
    Args:
        values: (dict) values to save.
        table_name: (string) data table's name.
        record_id: (string, optional) record's id. If it is empty, add a new record.
    """
    form_class = FORM_SET.get(table_name)
    if not form_class:
        raise MudderyError(ERR.no_table, "Can not find table: %s" % table_name)

    form = None
    record = None
    if record_id:
        try:
            # Query record's data.
            record = general_query_mapper.get_record_by_id(table_name, record_id)
            form = form_class(values, instance=record)
        except Exception, e:
            form = None

    if not form:
        # Get empty data.
        form = form_class(values)

    # Save data
    if form.is_valid():
        instance = form.save()
        return instance.pk
    else:
        raise MudderyError(ERR.invalid_form, "Invalid form.", data=form.errors)


def delete_record(table_name, record_id):
    """
    Delete a record of a table.
    """
    general_query_mapper.delete_record_by_id(table_name, record_id)
