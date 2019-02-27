"""
Query and deal common tables.
"""

from __future__ import print_function

from django.apps import apps
from django.conf import settings
from django.db import connections


def get_all_fields(table_name):
    """
    Get all columns informatin.

    Args:
        table_name: (string) db table's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj._meta.fields


def get_all_records(table_name):
    """
    Get a table's all records.

    Args:
        table_name: (string) db table's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj.objects.all()


def filter_records(table_name, **kwargs):
    """
    Filter records by conditions.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj.objects.filter(**kwargs)


def get_record_by_id(table_name, record_id):
    """
    Get a record by record's id.

    Args:
        table_name: (string) db table's name.
        record_id: (number) record's id.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj.objects.get(id=record_id)


def get_record_by_key(table_name, object_key):
    """
    Get a record by object's key.

    Args:
        table_name: (string) db table's name.
        object_key: (string) object's key.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj.objects.get(key=object_key)


def get_the_first_record(table_name):
    """
    Get a record by object's key.

    Args:
        table_name: (string) db table's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj.objects.first()


def get_the_last_record(table_name):
    """
    Get a record by object's key.

    Args:
        table_name: (string) db table's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj.objects.last()


def get_record(table_name, **kwargs):
    """
    Get a record by conditions.

    Args:
        table_name: (string) db table's name.
        kwargs: (dict) conditions.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    return model_obj.objects.get(**kwargs)


def delete_record_by_id(table_name, record_id):
    """
    Delete a record from a table by its id.

    Args:
        table_name: (string) db table's name.
        record_id: (number) record's id.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    record = model_obj.objects.get(id=record_id)
    record.delete()


def delete_record_by_key(table_name, object_key):
    """
    Delete a record from a table by its key.

    Args:
        table_name: (string) db table's name.
        object_key: (string) object's key.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)
    record = model_obj.objects.get(key=object_key)
    record.delete()


def get_all_from_tables(tables):
    """
    Query all object's data from tables.

    Args:
        tables: (string) table's list.

    Return:
        a dict of values.
    """
    if not tables or len(tables) <= 1:
        return

    # Get table's full name
    tables = [settings.WORLD_DATA_APP + "_" + table for table in tables]

    # join tables
    from_tables = ", ".join(tables)
    conditions = [tables[0] + ".key=" + t + ".key" for t in tables[1:]]
    conditions = " and ".join(conditions)
    query = "select * from %s where %s" % (from_tables, conditions)
    cursor = connections[settings.WORLD_DATA_APP].cursor()
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]

    # return records
    record = cursor.fetchone()
    while record is not None:
        yield dict(zip(columns, record))
        record = cursor.fetchone()
