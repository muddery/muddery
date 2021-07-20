"""
Battle commands. They only can be used when a character is in a combat.
"""

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from muddery.server.utils.exception import MudderyError, ERR
from muddery.worldeditor.dao import general_query_mapper
from muddery.worldeditor.dao.common_mappers import WORLD_AREAS, WORLD_ROOMS
from muddery.worldeditor.dao.system_data_mapper import SYSTEM_DATA
from muddery.worldeditor.dao.element_properties_mapper import ELEMENT_PROPERTIES
from muddery.worldeditor.mappings.form_set import FORM_SET
from muddery.server.mappings.element_set import ELEMENT, ELEMENT_SET
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.worldeditor.forms.location_field import LocationField
from muddery.worldeditor.forms.image_field import ImageField


def query_form(table_name, **kwargs):
    """
    Query table's data.

    Args:
        table_name: (string) data table's name.
        kwargs: (dict) conditions.
    """
    form_class = FORM_SET.get(table_name)
    if not form_class:
        raise MudderyError(ERR.no_table, "Can not find table: %s" % table_name)

    form = None
    record = None
    if kwargs:
        try:
            # Query record's data.
            record = general_query_mapper.get_record(table_name, **kwargs)
            form = form_class(instance=record)
        except Exception as e:
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
        "value": record.id if record else "",
    })

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
        elif isinstance(field, ImageField):
            info["type"] = "Image"
            info["image_type"] = field.get_type()

        fields.append(info)

    return fields


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
    if record_id:
        try:
            # Query record's data.
            record = general_query_mapper.get_record_by_id(table_name, record_id)
            form = form_class(values, instance=record)
        except Exception as e:
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


def delete_records(table_name, **kwargs):
    """
    Delete records by conditions.
    """
    general_query_mapper.delete_records(table_name, **kwargs)


def query_object_form(base_element_type, obj_element_type, obj_key):
    """
    Query all data of an object.

    Args:
        base_element_type: (string) the base element of the object.
        obj_element_type: (string, optional) object's element type. If it is empty, use the element type of the object
                        or use the base element type.
        obj_key: (string) object's key. If it is empty, query an empty form.
    """
    candidate_element_types = ELEMENT_SET.get_group(base_element_type)
    if not candidate_element_types:
        raise MudderyError(ERR.no_table, "Can not find the element: %s" % base_element_type)

    if not obj_element_type:
        # Or use the base element type
        obj_element_type = base_element_type

    element = ELEMENT_SET.get(obj_element_type)
    if not element:
        raise MudderyError(ERR.no_table, "Can not get the element: %s" % obj_element_type)
    table_names = element.get_models()

    forms = []
    for table_name in table_names:
        if obj_key:
            object_form = query_form(table_name, key=obj_key)
        else:
            object_form = query_form(table_name)

        forms.append({
            "table": table_name,
            "fields": object_form
        })

    # add elements
    if len(forms) > 0:
        for field in forms[0]["fields"]:
            if field["name"] == "element_type":
                # set the element type to the new value
                field["value"] = obj_element_type
                field["type"] = "Select"
                field["choices"] = [(key, element.element_name + " (" + key + ")")
                                    for key, element in candidate_element_types.items()]
                break

    return forms


def save_object_level_properties(object_key, level, values):
    """
    Save properties of an object.

    Args:
        object_key: (string) object' key.
        level: (number) object's level.
        values: (dict) values to save.
    """
    ELEMENT_PROPERTIES.add_properties(object_key, level, values)


def delete_object_level_properties(object_key, level):
    """
    Delete properties of a level of the given object.

    Args:
        object_key: (string) object' key.
        level: (number) object's level.
    """
    ELEMENT_PROPERTIES.delete_properties(object_key, level)


def save_object_form(tables, obj_element_type, obj_key):
    """
    Save all data of an object.

    Args:
        tables: (list) a list of table data.
               [{
                 "table": (string) table's name.
                 "record": (string, optional) record's id. If it is empty, add a new record.
                }]
        obj_element_type: (string) object's element type.
        obj_key: (string) current object's key. If it is empty or changed, query an empty form.
    """
    if not tables:
        raise MudderyError(ERR.invalid_form, "Invalid form.", data="Empty form.")

    # Get object's new key from the first form.
    try:
        new_key = tables[0]["values"]["key"]
    except KeyError:
        new_key = obj_key

    if not new_key:
        # Does not has a new key, generate a new key.
        index = SYSTEM_DATA.get_object_index()
        new_key = "%s_auto_%s" % (obj_element_type, index)
        for table in tables:
            table["values"]["key"] = new_key

    forms = []
    for table in tables:
        table_name = table["table"]
        form_values = table["values"]

        form_class = FORM_SET.get(table_name)
        form = None
        if obj_key:
            try:
                # Query the current object's data.
                record = general_query_mapper.get_record_by_key(table_name, obj_key)
                form = form_class(form_values, instance=record)
            except ObjectDoesNotExist:
                form = None

        if not form:
            # Get empty data.
            form = form_class(form_values)

        forms.append(form)

    # check data
    for form in forms:
        if not form.is_valid():
            raise MudderyError(ERR.invalid_form, "Invalid form.", data=form.errors)

    # Save data
    with transaction.atomic():
        for form in forms:
            form.save()

    return new_key


def save_map_positions(area, rooms):
    """
    Save all data of an object.

    Args:
        area: (dict) area's data.
        rooms: (dict) rooms' data.
    """
    with transaction.atomic():
        # area data
        record = WORLD_AREAS.get(key=area["key"])
        record.background = area["background"]
        record.width = area["width"]
        record.height = area["height"]

        record.full_clean()
        record.save()

        # rooms
        for room in rooms:
            position = ""
            if len(room["position"]) > 1:
                position = "(%s,%s)" % (room["position"][0], room["position"][1])
            record = WORLD_ROOMS.get(key=room["key"])
            record.position = position

            record.full_clean()
            record.save()


def delete_object(obj_key, base_element_type=None):
    """
    Delete an object from all tables under the base element type.
    """
    elements = ELEMENT_SET.get_group(base_element_type)
    tables = set()
    for key, value in elements.items():
        tables.update(value.get_models())

    with transaction.atomic():
        for table in tables:
            try:
                general_query_mapper.delete_record_by_key(table, obj_key)
            except ObjectDoesNotExist:
                pass


def query_event_action_forms(action_type, event_key):
    """
    Query forms of the event action.

    Args:
        action_type: (string) action's type
        event_key: (string) event's key
    """
    # Get action's data.
    action = EVENT_ACTION_SET.get(action_type)
    if not action:
        raise MudderyError(ERR.no_table, "Can not find action: %s" % action_type)

    # Get all forms.
    forms = []
    table_name = action.model_name
    records = general_query_mapper.filter_records(table_name, event_key=event_key)
    if records:
        for record in records:
            forms.append(query_form(table_name, id=record.id))
    else:
        forms.append(query_form(table_name))

    return {
        "forms": forms,
        "repeatedly": action.repeatedly
    }


def update_object_key(element_type, old_key, new_key):
    """
    Update an object's key in other tables.

    Args:
        element_type: (string) object's element type.
        old_key: (string) object's old key.
        new_key: (string) object's new key
    """
    # The object's key has changed.
    element = ELEMENT(element_type)
    if issubclass(element_type, ELEMENT("AREA")):
        # Update relative room's location.
        model_name = ELEMENT("ROOM").model_name
        if model_name:
            general_query_mapper.filter_records(model_name, area=old_key).update(area=new_key)
    elif issubclass(element_type, ELEMENT("ROOM")):
        # Update relative exit's location.
        model_name = ELEMENT("EXIT").model_name
        if model_name:
            general_query_mapper.filter_records(model_name, location=old_key).update(location=new_key)
            general_query_mapper.filter_records(model_name, destination=old_key).update(destination=new_key)

        # Update relative world object's location.
        model_name = ELEMENT("WORLD_OBJECT").model_name
        if model_name:
            general_query_mapper.filter_records(model_name, location=old_key).update(location=new_key)

        # Update relative world NPC's location.
        model_name = ELEMENT("WORLD_NPC").model_name
        if model_name:
            general_query_mapper.filter_records(model_name, location=old_key).update(location=new_key)
