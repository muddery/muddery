"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from django.db import transaction
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import logger
from muddery.utils import defines
from muddery.utils.exception import MudderyError, ERR
from muddery.utils.localized_strings_handler import _
from muddery.worlddata.dao import general_query_mapper
from muddery.worlddata.dao.common_mappers import OBJECTS
from muddery.mappings.form_set import FORM_SET
from muddery.mappings.typeclass_set import TYPECLASS, TYPECLASS_SET
from muddery.worlddata.forms.default_forms import ObjectsForm
from muddery.worlddata.forms.location_field import LocationField
from muddery.worlddata.forms.image_field import ImageField
from muddery.worlddata.services.general_query import query_fields


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


def query_object_form(base_typeclass, obj_typeclass, obj_key):
    """
    Query all data of an object.

    Args:
        base_typeclass: (string) candidate typeclass group.
        obj_typeclass: (string, optional) object's typeclass. If it is empty, use the typeclass of the object
                        or use base typeclass as object's typeclass.
        obj_key: (string) object's key. If it is empty, query an empty form.
    """
    candidate_typeclasses = TYPECLASS_SET.get_group(base_typeclass)
    if not candidate_typeclasses:
        raise MudderyError(ERR.no_table, "Can not find typeclass: %s" % base_typeclass)

    if not obj_typeclass:
        if obj_key:
            # Get typeclass from the object's record
            table_name = TYPECLASS("OBJECT").model_name
            record = general_query_mapper.get_record_by_key(table_name, obj_key)
            obj_typeclass = record.typeclass
        else:
            # Or use the base typeclass
            obj_typeclass = base_typeclass

    typeclass = TYPECLASS_SET.get(obj_typeclass)
    if not typeclass:
        raise MudderyError(ERR.no_table, "Can not find typeclass: %s" % obj_typeclass)
    table_names = typeclass.get_models()

    forms = []
    for table_name in table_names:
        if obj_key:
            object_form = query_form(table_name, key=obj_key)
        else:
            object_form = query_form(table_name)

        forms.append({"table": table_name,
                      "fields": object_form})

    # add typeclasses
    if len(forms) > 0:
        for field in forms[0]["fields"]:
            if field["name"] == "typeclass":
                # set typeclass to the new value
                field["value"] = obj_typeclass
                field["type"] = "Select"
                field["choices"] = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in candidate_typeclasses.items()]
                break

    return forms


def save_object_form(tables, obj_typeclass, obj_key):
    """
    Save all data of an object.

    Args:
        tables: (list) a list of table data.
               [{
                 "table": (string) table's name.
                 "record": (string, optional) record's id. If it is empty, add a new record.
                }]
        obj_typeclass: (string) object's typeclass.
        obj_key: (string) current object's key. If it is empty or changed, query an empty form.
    """
    if not tables:
        raise MudderyError(ERR.invalid_form, "Invalid form.", data="Empty form.")

    try:
        typeclass = TYPECLASS(obj_typeclass)
    except:
        raise MudderyError(ERR.invalid_form, "Invalid form.", data="No typeclass: %s" % obj_typeclass)

    # Get object's new key from the first form.
    new_obj = not (obj_key and obj_key == tables[0]["values"]["key"])
    if new_obj:
        try:
            obj_key = tables[0]["values"]["key"]
        except KeyError:
            pass

        if not obj_key:
            # Generate a new key.
            try:
                # Get object table's last id.
                query = general_query_mapper.get_the_last_record(typeclass.model_name)
                if query:
                    index = int(query.id) + 1
                else:
                    index = 1
            except Exception, e:
                raise MudderyError(ERR.invalid_form, "Invalid form.", data="No typeclass model: %s" % obj_typeclass)

            obj_key = obj_typeclass + "_" + str(index)

            for table in tables:
                table["values"]["key"] = obj_key

    forms = []
    for table in tables:
        table_name = table["table"]
        form_values = table["values"]

        form_class = FORM_SET.get(table_name)
        form = None
        if not new_obj:
            try:
                # Query record's data.
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


def delete_object(base_typeclass, obj_key):
    """
    Delete an object from all tables under the base typeclass.
    """
    typeclasses = TYPECLASS_SET.get_group(base_typeclass)
    tables = set()
    for key, value in typeclasses.items():
        tables.update(value.get_models())

    for table in tables:
        try:
            general_query_mapper.delete_record_by_key(table, obj_key)
        except ObjectDoesNotExist:
            pass
