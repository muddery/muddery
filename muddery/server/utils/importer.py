"""
This module imports data from files to db.
"""

import os, glob
import traceback
from sqlalchemy import delete
from muddery.common.utils.exception import MudderyError, ERR
from muddery.common.utils import readers
from muddery.server.database.worlddata_db import WorldDataDB
from muddery.server.utils.logger import logger


def import_file(fullname, file_type=None, table_name=None, clear=True, except_errors=False, **kwargs):
    """
    Import data from a data file to the db model

    Args:
        fullname: (string) file's full name
        file_type: (string) set file's type. If it's None, get the file's type from filename.
        table_name: (string) the type of the file. If it's None, the function will get
                   the file type from the extension name of the file.
        clear: (boolean) clear old data.
        except_errors: (boolean) except error records and load other records.
    """
    def get_field_types(model_obj, field_names):
        """
        Get field types by field names.

        type = 0    means common field
        type = 1    means Boolean field
        type = 2    means Integer field
        type = 3    means Float field
        type = 4    means ForeignKey field, not support
        type = 5    means ManyToManyField field, not support
        type = -1   means field does not exist
        """
        field_types = []
        for field_name in field_names:
            field_type = -1

            try:
                # get field info
                field = model_obj.__table__.columns[field_name]

                if field.type.python_type == bool:
                    field_type = 1
                elif field.type.python_type == int:
                    field_type = 2
                elif field.type.python_type == float:
                    field_type = 3
                else:
                    field_type = 0
            except Exception as e:
                field_type = -1
                logger.log_err("Field %s error: %s" % (field_name, e))

            field_types.append(field_type)

        return field_types

    def parse_record(field_names, field_types, values):
        """
        Parse text values to field values.
        """
        record = {}
        for item in zip(field_names, field_types, values):
            field_name = item[0]
            # skip "id" field
            if field_name == "id":
                continue

            field_type = item[1]
            value = item[2]

            try:
                # set field values
                if field_type == -1:
                    # not support this field
                    continue
                elif field_type == 0:
                    # default
                    record[field_name] = value
                elif field_type == 1:
                    # boolean value
                    if value:
                        upper = value.upper()
                        if upper == 'TRUE' or upper == 'T':
                            record[field_name] = True
                        elif upper == 'FALSE' or upper == 'F':
                            record[field_name] = False
                        else:
                            record[field_name] = (int(value) != 0)
                elif field_type == 2:
                    # interger value
                    if value:
                        record[field_name] = int(value)
                elif field_type == 3:
                    # float value
                    if value:
                        record[field_name] = float(value)
            except Exception as e:
                raise Exception("%s '%s' error: %s" % (field_name, value, e))

        return record

    def import_data(session, model, data_iterator):
        """
        Import data to a table.

        Args:
            model_obj: (model) model object.
            data_iterator: (list) data list.

        Returns:
            None
        """
        try:
            # read title
            titles = next(data_iterator)
            field_types = get_field_types(model, titles)

            # import values
            with session.begin():
                for index, values in enumerate(data_iterator):
                    # skip blank lines
                    if not "".join(values):
                        continue

                    try:
                        data = parse_record(titles, field_types, values)
                        record = model(**data)
                        session.add(record)
                        session.flush()
                    except Exception as e:
                        msg = "Import %s line %s error: %s" % (model.__tablename__, index + 2, e)
                        if except_errors:
                            print(msg)
                            logger.log_warn(msg)
                        else:
                            logger.log_err(msg)
                            raise MudderyError(ERR.import_data_error, msg)
        except StopIteration:
            # reach the end of file, pass this exception
            pass

    # separate name and ext name
    try:
        filename, ext_name = os.path.splitext(fullname)
        if not table_name:
            table_name = filename
        if not file_type:
            if ext_name:
                file_type = ext_name[1:].lower()
    except:
        pass

    # get model
    session = WorldDataDB.inst().get_session()
    model = WorldDataDB.inst().get_model(table_name)

    if clear:
        stmt = delete(model)
        session.execute(stmt)

    reader_class = readers.get_reader(file_type)
    if not reader_class:
        # Does support this file type.
        raise(MudderyError(ERR.import_data_error, "Unknown file type."))

    reader = reader_class(fullname)
    if not reader:
        # Does support this file type.
        raise(MudderyError(ERR.import_data_error, "Does not support this file type."))

    logger.log_debug("Importing %s" % table_name)
    try:
        import_data(session, model, reader)
    finally:
        reader.close()


def import_data_path(path, clear=True, except_errors=False):
    """
    Import data from path.

    Args:
        path: (string) data path.
        clear: (boolean) clear old data.
        except_errors: (boolean) except error records and load other records.
    """
    # import tables one by one
    tables = WorldDataDB.inst().get_tables()
    for table_name in tables:
        file_names = glob.glob(os.path.join(path, table_name) + ".*")

        if file_names:
            print("Importing %s" % file_names[0])
            import_file(file_names[0], table_name=table_name, clear=clear, except_errors=except_errors)


def import_table_path(path, table_name, clear=True, except_errors=False):
    """
    Import a table's data from a path.

    Args:
        path: (string) data path.
        table_name: (string) table's name.
        clear: (boolean) clear old data.
    """
    if clear:
        WorldDataDB.inst().clear_table(table_name)

    if not os.path.isdir(path):
        return

    for file_name in os.listdir(path):
        file_name = os.path.join(path, file_name)
        if os.path.isdir(file_name):
            # if it is a folder
            continue

        print("Importing %s" % file_name)
        try:
            import_file(file_name, table_name=table_name, clear=False, except_errors=except_errors)
        except Exception as e:
            print("Import error: %s" % e)
