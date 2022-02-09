"""
Query and deal common tables.
"""

import importlib
from sqlalchemy import select, delete, update, func
from muddery.server.mappings.element_set import ELEMENT
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.database.db_manager import DBManager
from muddery.worldeditor.dao.dict_record import DictRecord
from muddery.server.utils.logger import logger


def get_field_names(table_name):
    """
    Get all columns informatin.

    Args:
        table_name: (string) db table's name.
    """
    # get model
    model = DBManager.inst().get_model(SETTINGS.WORLD_DATA_APP, table_name)
    return model.__table__.columns.keys()


def count(table_name, condition=None):
    """
    Count the number of records with conditions in kwargs.
    """
    session_name = SETTINGS.WORLD_DATA_APP
    session = DBManager.inst().get_session(session_name)
    model = DBManager.inst().get_model(session_name, table_name)

    stmt = select(func.count()).select_from(model)
    for field, value in condition.items():
        stmt = stmt.where(getattr(model, field) == value)

    result = session.execute(stmt)
    return result.scalars().all()[0]


def get_query(table_name, condition=None):
    """
    Get a query of given condition.
    """
    session_name = SETTINGS.WORLD_DATA_APP
    session = DBManager.inst().get_session(session_name)
    model = DBManager.inst().get_model(session_name, table_name)

    # set conditions
    stmt = select(model)

    if condition:
        where_condition = [(getattr(model, field)) == value for field, value in condition.items()]
        stmt = stmt.where(*where_condition)

    result = session.execute(stmt)
    return result.scalars()


def get_one(table_name, condition=None):
    """
    Get a record of given condition. Compatible with the wtforms_alchemy's unique validator.
    """
    session_name = SETTINGS.WORLD_DATA_APP
    session = DBManager.inst().get_session(session_name)
    model = DBManager.inst().get_model(session_name, table_name)

    # set conditions
    stmt = session.query(model)

    if condition:
        where_condition = [(getattr(model, field)) == value for field, value in condition.items()]
        stmt = stmt.filter(*where_condition)

    result = stmt.first()
    return result


def filter_records(table_name, condition=None):
    """
    Filter records by conditions.
    """
    query = get_query(table_name, condition)
    return query


def get_record(table_name, condition=None):
    """
    Get a record by conditions.

    Args:
        table_name: (string) db table's name.
        condition: (dict) conditions.
    """
    query = get_query(table_name, condition)
    return query.one()


def get_the_first_record(table_name):
    """
    Get a record by object's key.

    Args:
        table_name: (string) db table's name.
    """
    # get model
    query = get_query(table_name)
    return query.first()


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
    return get_record(table_name, {"id": record_id})


def get_record_by_key(table_name, object_key):
    """
    Get a record by object's key.

    Args:
        table_name: (string) db table's name.
        object_key: (string) object's key.
    """
    # get model
    return get_record(table_name, {"key": object_key})


def delete_records(table_name, condition=None):
    """
    Delete records with the given conditions.
    """
    session_name = SETTINGS.WORLD_DATA_APP
    session = DBManager.inst().get_session(session_name)
    model = DBManager.inst().get_model(session_name, table_name)

    # set conditions
    stmt = delete(model)
    if condition:
        where_condition = [(getattr(model, field)) == value for field, value in condition.items()]
        stmt = stmt.where(*where_condition)

    result = session.execute(stmt)
    return result.rowcount


def delete_record_by_id(table_name, record_id):
    """
    Delete a record from a table by its id.

    Args:
        table_name: (string) db table's name.
        record_id: (number) record's id.
    """
    # get model
    delete_records(table_name, {"id": record_id})


def delete_record_by_key(table_name, object_key):
    """
    Delete a record from a table by its key.

    Args:
        table_name: (string) db table's name.
        object_key: (string) object's key.
    """
    # get model
    delete_records(table_name, {"key": object_key})


def get_all_from_tables(tables, condition=None):
    """
    Query all object's data from tables.

    Args:
        tables: (string) table's list.

    Return:
        a dict of values.
    """
    if not tables:
        return

    session_name = SETTINGS.WORLD_DATA_APP
    session = DBManager.inst().get_session(session_name)
    config = SETTINGS.DATABASES[session_name]
    module = importlib.import_module(config["MODELS"])

    if len(tables) == 1:
        # only one table
        model = getattr(module, tables[0])
        stmt = select(model)

        if condition:
            where_condition = [(getattr(model, field)) == value for field, value in condition.items()]
            stmt = stmt.where(*where_condition)
    else:
        # join tables
        models = [getattr(module, t) for t in tables]
        stmt = select(*models)

        if condition:
            where_condition = [(getattr(models[0], field)) == value for field, value in condition.items()]
            stmt = stmt.where(*where_condition)

        first_model = models[0]
        for model in models[1:]:
            stmt = stmt.join(model, getattr(first_model, "key") == getattr(model, "key"))

    result = session.execute(stmt)
    records = result.all()

    # put data in a list of MemoryRecord
    data = []
    for record in records:
        data.append(DictRecord({
            field: getattr(model, field)
            for model in record
            for field in model.__table__.columns.keys()
        }))

    return data


def get_tables_record_by_key(tables, key):
    """
    Filter object's data from tables.

    Args:
        tables: (string) table's list.
        key: (string) object's key.

    Return:
        a dict of values.
    """
    return get_all_from_tables(tables, {"key": key})


def get_element_base_data(element_type):
    """
    Query the base data of an element_type.

    :param element_type:
    :return:
    """
    base_model = ELEMENT(element_type).get_base_model()
    return filter_records(base_model, {"element_type": element_type})


def delete_tables_record_by_key(tables, key):
    """
    Delete object's data from tables.

    Args:
        tables: (string) table's list.
        key: (string) object's key.

    Return:
        a dict of values.
    """
    session_name = SETTINGS.WORLD_DATA_APP
    session = DBManager.inst().get_session(session_name)

    with session.begin():
        for table_name in tables:
            model = DBManager.inst().get_model(session_name, table_name)

            # set conditions
            stmt = delete(model).where(model.key==key)
            session.execute(stmt)

    return


def update_records(table_name, values, condition=None):
    """
    Update records with given values.

    Args:
        table_name: (string) the name of a table
        values: (dict) keys and values to update
        condition: (dict) update conditions
    """
    session_name = SETTINGS.WORLD_DATA_APP
    session = DBManager.inst().get_session(session_name)
    model = DBManager.inst().get_model(session_name, table_name)

    # set conditions
    stmt = update(model).values(**values)
    if condition:
        where_condition = [(getattr(model, field)) == value for field, value in condition.items()]
        stmt = stmt.where(*where_condition)

    result = session.execute(stmt)
    return result.rowcount
