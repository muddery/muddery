"""
Import table data.
"""

import os, traceback
from sqlalchemy import delete
from muddery.server.utils.logger import logger
from muddery.server.utils.exception import MudderyError, ERR
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.utils import readers
from muddery.worldeditor.database.db_manager import DBManager


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
                        if value == 'True':
                            record[field_name] = True
                        elif value == 'False':
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
                raise Exception({field_name: "value error: '%s'" % value})

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
        line = 1
        try:
            # read title
            titles = next(data_iterator)
            field_types = get_field_types(model, titles)
            line += 1

            # import values
            with session.begin():
                for values in data_iterator:
                    # skip blank lines
                    blank_line = True
                    for value in values:
                        if value:
                            blank_line = False
                            break
                    if blank_line:
                        line += 1
                        continue

                    data = parse_record(titles, field_types, values)
                    record = model(**data)
                    session.add(record)
                    line += 1

        except StopIteration:
            # reach the end of file, pass this exception
            pass
        #except ValidationError as e:
        #    traceback.print_exc()
        #    raise MudderyError(ERR.import_data_error, parse_error(e, model_obj.__name__, line))
        except Exception as e:
            traceback.print_exc()
            raise MudderyError(ERR.import_data_error, "%s (model: %s, line: %s)" % (e, model.__tablename__, line))

    def parse_error(error, model_name, line):
        """
        Parse validation error to string message.

        Args:
            error: (ValidationError) a ValidationError.
            line: (number) the line number where the error occurs.
        Returns:
            (string) output string.
        """
        err_message = ""

        if hasattr(error, "error_dict"):
            error_dict = error.error_dict
        else:
            error_dict = {"": error.error_list}

        count = 1
        for field, error_list in error_dict.items():
            err_message += str(count) + ". "
            if field:
                err_message += "[" + field + "] "
            for item in error_list:
                if item.params:
                    err_message += item.message % item.params + "  "
                else:
                    err_message += item.message + "  "
            count += 1
        return "%s (model: %s, line: %s)" % (err_message, model_name, line)

    # separate name and ext name
    (filename, ext_name) = os.path.splitext(fullname)
    if not table_name:
        table_name = filename
    if not file_type:
        if ext_name:
            file_type = ext_name[1:].lower()

    # get model
    session = DBManager.inst().get_session(SETTINGS.WORLD_DATA_APP)
    model = DBManager.inst().get_model(SETTINGS.WORLD_DATA_APP, table_name)

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

    logger.log_info("Importing %s" % table_name)
    import_data(session, model, reader)
