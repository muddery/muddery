"""
Create sqlalchemy engines.
"""

from sqlalchemy import create_engine


def get_engine(db_type, configs):
    """
    Get an engine according to the database type.
    """
    db_link = get_db_link(db_type, configs)
    return create_engine(db_link, echo=configs["DEBUG"])


def get_db_link(db_type, configs):
    if db_type == "sqlite3":
        return get_sqlite3_link(configs)
    elif db_type == "mysql":
        return get_mysql_link(configs)


def get_sqlite3_link(configs):
    """
    Get a sqlite3 engine with configs.
    """
    link = "sqlite:///{path}?check_same_thread=False".format(path=configs["NAME"])
    return link


def get_mysql_link(configs):
    """
    Get a mysql engine with configs.
    mysql+pymysql://root:*@localhost:3306/blog?charset=utf8

    """
    link = "mysql+pymysql://{user}:{password}@{host}{port}/{name}".format(
               user=configs["USER"],
               password=configs["PASSWORD"],
               host=configs["HOST"] if configs["HOST"] else "localhost",
               port=(":%s" % configs["PORT"]) if configs["PORT"] else "",
               name=configs["NAME"]
           )

    return link
