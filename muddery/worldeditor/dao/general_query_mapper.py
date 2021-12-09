"""
Query and deal common tables.
"""

import importlib
from django.conf import settings
from django.db import connections
from django.core.exceptions import ObjectDoesNotExist
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.database.manager import Manager


def get_all_fields(table_name):
    """
    Get all columns informatin.

    Args:
        table_name: (string) db table's name.
    """
    # get model
    session_name = settings.WORLD_DATA_MODEL_FILE
    module = importlib.import_module(session_name)
    model = getattr(module, table_name)
    return model.__table__.columns.keys()


def get_query(table_name, **kwargs):
    """
    Get a query of given contidions.
    """
    session_name = settings.WORLD_DATA_MODEL_FILE
    session = Manager.instance().get_session(session_name)
    module = importlib.import_module(session_name)
    model = getattr(module, table_name)

    # set conditions
    query = session.query(model)
    if kwargs:
        for field, value in kwargs:
            query = query.filter(getattr(model, field) == value)

    return query


def filter_records(table_name, **kwargs):
    """
    Filter records by conditions.
    """
    query = get_query(table_name, **kwargs)
    return query.all()


def get_record(table_name, **kwargs):
    """
    Get a record by conditions.

    Args:
        table_name: (string) db table's name.
        kwargs: (dict) conditions.
    """
    query = get_query(table_name, **kwargs)
    return query.one()


def get_the_first_record(table_name):
    """
    Get a record by object's key.

    Args:
        table_name: (string) db table's name.
    """
    # get model
    query = get_query(table_name)
    return query.objects.first()


def get_all_records(table_name):
    """
    Get a table's all records.

    Args:
        table_name: (string) db table's name.
    """
    return filter_records(table_name)


def get_record_by_id(table_name, record_id):
    """
    Get a record by record's id.

    Args:
        table_name: (string) db table's name.
        record_id: (number) record's id.
    """
    return get_record(table_name, id=record_id)


def get_record_by_key(table_name, object_key):
    """
    Get a record by object's key.

    Args:
        table_name: (string) db table's name.
        object_key: (string) object's key.
    """
    # get model
    return get_record(table_name, key=object_key)


def delete_record_by_id(table_name, record_id):
    """
    Delete a record from a table by its id.

    Args:
        table_name: (string) db table's name.
        record_id: (number) record's id.
    """
    # get model
    record = get_record_by_id(table_name, record_id)
    record.delete()


def delete_record_by_key(table_name, object_key):
    """
    Delete a record from a table by its key.

    Args:
        table_name: (string) db table's name.
        object_key: (string) object's key.
    """
    # get model
    record = get_record_by_key(table_name, object_key)
    record.delete()


def delete_records(table_name, **kwargs):
    """
    Delete records by conditions.

    Args:
        table_name: (string) db table's name.
        kwargs: (dict) conditions.
    """
    # get model
    records = filter_records(table_name, **kwargs)
    records.delete()


def get_all_from_tables(tables):
    """
    Query all object's data from tables.

    Args:
        tables: (string) table's list.

    Return:
        a dict of values.
    """
    if not tables:
        return

    # Get table's full name
    tables = [settings.WORLD_DATA_APP + "_" + table for table in tables]

    if len(tables) == 1:
        # only one table
        query = "select * from %s" % tables[0]
    else:
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


def get_tables_record_by_key(tables, key):
    """
    Filter object's data from tables.

    Args:
        tables: (string) table's list.
        key: (string) object's key.

    Return:
        a dict of values.
    """
    if not tables:
        return

    # Get table's full name
    tables = [settings.WORLD_DATA_APP + "_" + table for table in tables]

    if len(tables) == 1:
        query = "select * from %(tables)s where %(tables)s.key=%%s" % {"tables": tables[0]}
    else:
        # join tables
        from_tables = ", ".join(tables)
        conditions = [tables[0] + ".key=" + t + ".key" for t in tables[1:]]
        conditions = " and ".join(conditions)
        query = "select * from %(tables)s where %(first_table)s.key=%%s and %(join)s" %\
                    {"tables": from_tables,
                     "first_table": tables[0],
                     "join": conditions}

    cursor = connections[settings.WORLD_DATA_APP].cursor()
    cursor.execute(query, [key])
    columns = [col[0] for col in cursor.description]

    # return records
    record = cursor.fetchone()
    if record:
        return dict(zip(columns, record))
    else:
        raise ObjectDoesNotExist


def get_element_base_data(element_type):
    """
    Query the base data of an element_type.

    :param element_type:
    :return:
    """
    base_model = ELEMENT(element_type).get_base_model()
    return filter_records(base_model, element_type=element_type)
