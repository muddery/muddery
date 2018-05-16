"""
Import table data.
"""

from __future__ import print_function

import os, traceback
from django.apps import apps
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from evennia.utils import logger
from muddery.utils import readers
from muddery.utils.exception import MudderyError, ERR


def import_file(fullname, file_type=None, table_name=None, clear=True, **kwargs):
    """
    Import data from a data file to the db model

    Args:
        fullname: (string) file's full name
        table_name: (string) the type of the file. If it's None, the function will get
                   the file type from the extension name of the file.
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
                field = model_obj._meta.get_field(field_name)

                if isinstance(field, models.BooleanField):
                    field_type = 1
                elif isinstance(field, models.IntegerField):
                    field_type = 2
                elif isinstance(field, models.FloatField):
                    field_type = 3
                elif isinstance(field, models.ForeignKey):
                    field_type = 4
                elif isinstance(field, models.ManyToManyField):
                    field_type = 5
                else:
                    field_type = 0
            except Exception, e:
                field_type = -1
                logger.log_errmsg("Field %s error: %s" % (field_name, e))

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
            except Exception, e:
                raise ValidationError({field_name: "value error: '%s'" % value})

        return record

    def import_data(model_obj, data_iterator):
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
            titles = data_iterator.next()
            field_types = get_field_types(model_obj, titles)            
            line += 1

            # import values
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

                record = parse_record(titles, field_types, values)
                data = model_obj(**record)
                data.full_clean()
                data.save()
                line += 1

        except StopIteration:
            # reach the end of file, pass this exception
            pass
        """
        except ValidationError, e:
            traceback.print_stack()
            raise MudderyError(ERR.import_data_error, parse_error(e, model_obj.__name__, line))
        except Exception, e:
            traceback.print_stack()
            raise MudderyError(ERR.import_data_error, "%s (model: %s, line: %s)" % (e, model_obj.__name__, line))
        """

    def clear_model_data(model_obj, **kwargs):
        """
        Remove all data from db.

        Args:
            model_obj: model object.

        Returns:
            None
        """
        # clear old data
        model_obj.objects.all().delete()

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
                print("item.message: %s" % item.message)
                print("item.params: %s" % item.params)
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
    model_obj = apps.get_model(settings.WORLD_DATA_APP, table_name)

    if clear:
        clear_model_data(model_obj, **kwargs)

    reader_class = readers.get_reader(file_type)
    if not reader_class:
        # Does support this file type.
        raise(MudderyError(ERR.import_data_error, "Unknown file type."))

    reader = reader_class(fullname)
    if not reader:
        # Does support this file type.
        raise(MudderyError(ERR.import_data_error, "Does not support this file type."))

    logger.log_infomsg("Importing %s" % table_name)
    import_data(model_obj, reader)

