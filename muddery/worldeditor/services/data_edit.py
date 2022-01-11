"""
Battle commands. They only can be used when a character is in a combat.
"""

from muddery.server.conf import settings
from wtforms_alchemy.validators import Unique
from muddery.server.utils.logger import logger
from muddery.server.utils.exception import MudderyError, ERR
from muddery.worldeditor.dao import general_querys
from muddery.worldeditor.dao.system_data_mapper import SystemDataMapper
from muddery.worldeditor.dao.element_properties_mapper import ElementPropertiesMapper
from muddery.worldeditor.mappings.form_set import FORM_SET
from muddery.server.mappings.element_set import ELEMENT, ELEMENT_SET
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.server.utils.localized_strings_handler import _
from muddery.worldeditor.database.db_manager import DBManager
from muddery.worldeditor.forms.base_form import FormData


def query_form(table_name, condition=None):
    """
    Query table's data.

    Args:
        table_name: (string) data table's name.
        condition: (dict) conditions.
    """
    form_class = FORM_SET.get(table_name)
    if not form_class:
        raise MudderyError(ERR.no_table, "Can not find table: %s" % table_name)

    form = None
    record = None
    if condition:
        try:
            # Query record's data.
            record = general_querys.get_record(table_name, condition)
            form = form_class(obj=record)
        except Exception as e:
            form = None

    if not form:
        # Get empty data.
        form = form_class()

    field_names = general_querys.get_field_names(table_name)
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

        if record:
            info["value"] = getattr(record, field.id)

        if info["type"] == "Select":
            info["choices"] = field.choices
        elif info["type"] == "ImageInput":
            info["image_type"] = field.image_type

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

    form_data = FormData(values)

    is_new = True
    if record_id:
        try:
            # Query record's data.
            record = general_querys.get_record_by_id(table_name, record_id)
            form = form_class(formdata=form_data, obj=record)
            form.populate_obj(record)
            is_new = False
        except Exception as e:
            pass

    if is_new:
        model = DBManager.inst().get_model(settings.WORLD_DATA_APP, table_name)
        record = model(**values)
        form = form_class(formdata=form_data)

    # check data
    if not form.validate():
        raise MudderyError(ERR.invalid_form, "Invalid form.", data=form.errors)

    # Save data
    session = DBManager.inst().get_session(settings.WORLD_DATA_APP)
    try:
        if is_new:
            session.add(record)
        else:
            session.merge(record)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.log_trace("Can not save form %s" % e)
        raise

    return record.id


def delete_record(table_name, record_id):
    """
    Delete a record of a table.
    """
    general_querys.delete_record_by_id(table_name, record_id)


def delete_records(table_name, condition=None):
    """
    Delete records by conditions.
    """
    general_querys.delete_records(table_name, condition)


def query_element_form(base_element_type, obj_element_type, element_key):
    """
    Query all data of an object.

    Args:
        base_element_type: (string) the base element of the object.
        obj_element_type: (string, optional) object's element type. If it is empty, use the element type of the object
                        or use the base element type.
        element_key: (string) the element's key. If it is empty, query an empty form.
    """
    candidate_element_types = ELEMENT_SET.get_group(base_element_type)
    if not candidate_element_types:
        raise MudderyError(ERR.no_table, "Can not find the element: %s" % base_element_type)

    element = ELEMENT_SET.get(obj_element_type)
    if not element:
        raise MudderyError(ERR.no_table, "Can not get the element: %s" % obj_element_type)
    table_names = element.get_models()

    forms = []
    for table_name in table_names:
        if element_key:
            object_form = query_form(table_name, {"key": element_key})
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
                field["choices"] = [(key, _(element.element_name, "elements") + " (" + key + ")")
                                    for key, element in candidate_element_types.items()]
                break

    return forms


def save_element_level_properties(element_type, element_key, level, values):
    """
    Save properties of an element.

    Args:
        element_type: (string) the element's type.
        element_key: (string) the element's key.
        level: (number) object's level.
        values: (dict) values to save.
    """
    ElementPropertiesMapper.inst().add_properties(element_type, element_key, level, values)


def delete_element_level_properties(element_type, element_key, level):
    """
    Delete properties of a level of the element.

    Args:
        element_type: (string) the element's type.
        element_key: (string) the element's key.
        level: (number) object's level.
    """
    ElementPropertiesMapper.inst().delete_properties(element_type, element_key, level)


def save_element_form(tables, element_type, element_key):
    """
    Save all data of an object.

    Args:
        tables: (list) a list of table data.
               [{
                 "table": (string) table's name.
                 "record": (string, optional) record's id. If it is empty, add a new record.
                }]
        element_type: (string) element's type.
        element_key: (string) current element's key. If it is empty or changed, query an empty form.
    """
    if not tables:
        raise MudderyError(ERR.invalid_form, "Invalid form.", data="Empty form.")

    # Get object's new key from the first form.
    try:
        new_key = tables[0]["values"]["key"]
    except KeyError:
        new_key = element_key

    if not new_key:
        # Does not has a new key, generate a new key.
        index = SystemDataMapper.inst().get_object_index()
        new_key = "%s_auto_%s" % (element_type, index)
        for table in tables:
            table["values"]["key"] = new_key

    forms_to_save = []
    for table in tables:
        table_name = table["table"]
        values = table["values"]

        form_class = FORM_SET.get(table_name)
        if not form_class:
            raise MudderyError(ERR.no_table, "Can not find table: %s" % table_name)

        form_data = FormData(values)

        is_new = True
        form = None
        if element_key:
            try:
                # Query record's data.
                record = general_querys.get_record_by_key(table_name, element_key)
                form = form_class(formdata=form_data, obj=record)
                form.populate_obj(record)
                is_new = False
            except Exception as e:
                pass

        if is_new:
            model = DBManager.inst().get_model(settings.WORLD_DATA_APP, table_name)
            record = model(**values)
            form = form_class(formdata=form_data)

        # check data
        if not form.validate():
            raise MudderyError(ERR.invalid_form, "Invalid form.", data=form.errors)

        forms_to_save.append({
            "table_name": table_name,
            "record": record,
            "is_new": is_new,
            "id": values["id"] if not is_new else None,
        })

    # Save data.
    session = DBManager.inst().get_session(settings.WORLD_DATA_APP)
    try:
        for item in forms_to_save:
            if item["is_new"]:
                session.add(record)
            else:
                session.merge(record)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.log_trace("Can not save form %s" % e)
        raise

    return new_key


def save_map_positions(area, rooms):
    """
    Save all data of an object.

    Args:
        area: (dict) area's data.
        rooms: (dict) rooms' data.
    """
    # area data
    general_querys.update_records("world_areas", {
        "background": area["background"],
        "width": area["width"],
        "height": area["height"],
    }, condition={
        "key": area["key"]
    }, commit=False)

    # rooms
    for room in rooms:
        position = ""
        if len(room["position"]) > 1:
            position = "(%s,%s)" % (room["position"][0], room["position"][1])

        general_querys.update_records("world_rooms", {
            "position": position,
        }, condition={
            "key": room["key"],
        }, commit=False)

    session = DBManager.inst().get_session(settings.WORLD_DATA_APP)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.log_trace("Can not save map %s" % e)
        raise


def delete_element(element_key, base_element_type=None):
    """
    Delete an element from all tables under the base element type.
    """
    elements = ELEMENT_SET.get_group(base_element_type)
    tables = set()
    for key, value in elements.items():
        tables.update(value.get_models())

    general_querys.delete_tables_record_by_key(tables, element_key)


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
    records = general_querys.filter_records(table_name, condition={
        "event_key": event_key
    })

    for record in records:
        forms.append(query_form(table_name, {"id": record.id}))

    if not forms:
        forms.append(query_form(table_name))

    return {
        "forms": forms,
        "repeatedly": action.repeatedly
    }


def update_element_key(element_type, old_key, new_key):
    """
    Update an element's key in relative tables.

    Args:
        element_type: (string) object's element type.
        old_key: (string) object's old key.
        new_key: (string) object's new key
    """
    # The object's key has changed.
    element = ELEMENT(element_type)
    if issubclass(element, ELEMENT("AREA")):
        # Update relative room's location.
        model_name = ELEMENT("ROOM").model_name
        if model_name:
            general_querys.update_records(model_name, {"area": new_key}, condition={"area": old_key})
    elif issubclass(element, ELEMENT("ROOM")):
        # Update relative exit's location.
        model_name = ELEMENT("EXIT").model_name
        if model_name:
            general_querys.update_records(model_name, {"location": new_key}, condition={"location": old_key})
            general_querys.update_records(model_name, {"destination": new_key}, condition={"destination": old_key})

        # Update relative world object's location.
        model_name = ELEMENT("WORLD_OBJECT").model_name
        if model_name:
            general_querys.update_records(model_name, {"location": new_key}, condition={"location": old_key})

        # Update relative world NPC's location.
        model_name = ELEMENT("WORLD_NPC").model_name
        if model_name:
            general_querys.update_records(model_name, {"location": new_key}, condition={"location": old_key})
