"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from muddery.utils import defines
from muddery.utils.exception import MudderyError, ERR
from muddery.utils.localized_strings_handler import _
from muddery.worlddata.dao import general_query_mapper
from muddery.mappings.form_set import FORM_SET
from muddery.mappings.typeclass_set import TYPECLASS_SET
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


def query_object_form(typeclass_key, object_key):
    """
    Query table's data.

    Args:
        typeclass_key: (string) typeclass's name.
        object_key: (string, optional) object's key. If it is empty, query an empty form.
    """
    typeclass = TYPECLASS_SET.get(typeclass_key)
    if not typeclass:
        raise MudderyError(ERR.no_table, "Can not find typeclass: %s" % typeclass_key)

    typeclasses = TYPECLASS_SET.get_group(typeclass_key)

    forms = []
    table_names = typeclass.get_models()
    for table_name in table_names:
        if object_key:
            object_form = query_form(table_name, key=object_key)
        else:
            object_form = query_form(table_name)

        forms.append({"table": table_name,
                      "fields": object_form})

    # add typeclasses
    if forms and "typeclass" in forms[0]:
        forms[0]["type"] = "Select"
        forms[0]["choices"] = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]

    return forms


