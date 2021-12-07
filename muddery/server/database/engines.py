"""
Create sqlalchemy engines.
"""

from sqlalchemy import create_engine


def get_engine(type, configs):
    """
    Get an engine according to the database type.
    """
    if type=="sqlite3":
        return get_sqlite3_engine(configs)


def get_sqlite3_engine(configs):
    """
    Get an sqlite3 engine with configs.
    """
    link = "sqlite:///" + configs["NAME"] + "?check_same_thread=False"
    return create_engine(link, echo=configs["DEBUG"])