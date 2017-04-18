"""
This module defines available model types.
"""
import os
import glob
import traceback
from django.apps import apps
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from evennia.utils import logger
from muddery.utils import readers
from muddery.utils.exception import MudderyError


class DataHandler(object):
    """

    """
    def __init__(self, model_name):
        """

        Args:
            model_name:

        Returns:

        """
        self.model_name = model_name
        self.model = None
        self.objects = None
        
        try:
            self.model = apps.get_model(settings.WORLD_DATA_APP, self.model_name)
            self.objects = self.model.objects
        except Exception, e:
            ostring = "Can not load model %s: %s" % (self.model_name, e)
            print(ostring)
            logger.log_errmsg(ostring)

    def get_field_types(self, model_obj, field_names):
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

    def parse_record(self, field_names, field_types, values):
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

    def import_data(self, reader, **kwargs):
        """
        Import data to the model.

        Args:
            reader:

        Returns:
            None
        """
        line = 1
        try:
            # read title
            titles = reader.next()
            field_types = self.get_field_types(self.model, titles)            
            line += 1

            # import values
            for values in reader:
                # skip blank lines
                blank_line = True
                for value in values:
                    if value:
                        blank_line = False
                        break
                if blank_line:
                    line += 1
                    continue

                record = self.parse_record(titles, field_types, values)
                data = self.model(**record)
                data.full_clean()
                data.save()
                line += 1

        except StopIteration:
            # reach the end of file, pass this exception
            pass
        except ValidationError, e:
            raise MudderyError(self.parse_error(e, line))
        except Exception, e:
            raise MudderyError("%s (model: %s, line: %s)" % (e, self.model_name, line))

    def import_file(self, file_name, file_type=None, clear=True, **kwargs):
        """
        Import data from a data file to the db model

        Args:
            file_name: (string) file's name
            file_type: (string) the type of the file. If it's None, the function will get
                       the file type from the extension name of the file.
        """
        if clear:
            self.clear_model_data(**kwargs)

        # get file list
        if not file_type:
            # find extensions
            file_names = glob.glob(file_name + ".*")

            # add original filename
            file_names.append(file_name)
        else:
            file_names = [file_name]

        for file_name in file_names:
            if not file_type:
                # get file's extension name as file type
                file_type = os.path.splitext(file_name)[1].lower()
                if len(file_type) > 0:
                    file_type = file_type[1:]

            reader_class = readers.get_reader(file_type)
            if not reader_class:
                # Does support this file type, read next one.
                continue

            reader = reader_class(file_name)
            if not reader:
                # Does support this file type, read next one.
                continue

            print("Importing %s" % file_name)
            self.import_data(reader, **kwargs)
            break

    def import_from_path(self, path_name, **kwargs):
        """

        Args:
            path_name:
            system_data:

        Returns:

        """
        file_name = os.path.join(path_name, self.model_name)
        return self.import_file(file_name, **kwargs)

    def clear_model_data(self, **kwargs):
        """
        Remove all data from db.

        Args:
            model_name: (string) db model's name.

        Returns:
            None
        """
        # clear old data
        self.objects.all().delete()

    def parse_error(self, error, line):
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
                err_message += item.message % item.params + "  "
            count += 1
        return "%s (model: %s, line: %s)" % (err_message, self.model_name, line)


class SystemDataHandler(DataHandler):
    """

    """
    def import_data(self, reader, **kwargs):
        """
        Import data to the model.

        Args:
            model_obj:
            reader:

        Returns:
            None
        """
        system_data = kwargs.get('system_data', False)
        
        line = 1
        try:
            # read title
            titles = reader.next()

            field_types = self.get_field_types(self.model, titles)

            key_index = -1
            # get pk's position
            for index, title in enumerate(titles):
                if title == "key":
                    key_index = index
                    break
            if key_index == -1:
                print("Can not found system data's key.")
                return
                
            line += 1

            # import values
            for values in reader:
                # skip blank lines
                blank_line = True
                for value in values:
                    if value:
                        blank_line = False
                        break
                if blank_line:
                    line += 1
                    continue

                record = self.parse_record(titles, field_types, values)
                key = values[key_index]

                # Merge system and custom data.
                if system_data:
                    # System data can not overwrite custom data.
                    if self.model.objects.filter(key=key, system_data=False).count() > 0:
                        continue

                    # Add system data flag.
                    record["system_data"] = True
                else:
                    # Custom data can not overwrite system data.
                    self.model.objects.filter(key=key, system_data=True).delete()

                data = self.model(**record)
                data.full_clean()
                data.save()
                line += 1

        except StopIteration:
            # reach the end of file, pass this exception
            pass
        except ValidationError, e:
            raise MudderyError(self.parse_error(e, line))
        except Exception, e:
            raise MudderyError("%s (model: %s, line: %s)" % (e, self.model_name, line))

    def clear_model_data(self, **kwargs):
        """
        Remove all data from db.

        Args:
            model_name: (string) db model's name.

        Returns:
            None
        """
        system_data = kwargs.get('system_data', False)
        
        # clear old data
        self.objects.filter(system_data=system_data).delete()


class LocalizedStringsHandler(DataHandler):
    """

    """
    def import_data(self, reader, **kwargs):
        """
        Import data to the model.

        Args:
            model_obj:
            reader:

        Returns:
            None
        """
        system_data = kwargs.get('system_data', False)

        line = 1
        try:
            # read title
            titles = reader.next()

            field_types = self.get_field_types(self.model, titles)

            category_index = -1
            origin_index = -1
            if system_data:
                # get pk's position
                for index, title in enumerate(titles):
                    if title == "category":
                        category_index = index
                    elif title == "origin":
                        origin_index = index
                if category_index == -1 and origin_index == -1:
                    print("Can not found data's key.")
                    return
                    
            line += 1

            # import values
            for values in reader:
                # skip blank lines
                blank_line = True
                for value in values:
                    if value:
                        blank_line = False
                        break
                if blank_line:
                    line += 1
                    continue

                record = self.parse_record(titles, field_types, values)
                category = values[category_index]
                origin = values[origin_index]

                # Merge system and custom data.
                if system_data:
                    # System data can not overwrite custom data.
                    if self.model.objects.filter(category=category, origin=origin, system_data=False).count() > 0:
                        continue

                    # Add system data flag.
                    record["system_data"] = True
                else:
                    # Custom data can not overwrite system data.
                    self.model.objects.filter(category=category, origin=origin, system_data=True).delete()

                data = self.model(**record)
                data.full_clean()
                data.save()
                line += 1

        except StopIteration:
            # reach the end of file, pass this exception
            pass
        except ValidationError, e:
            raise MudderyError(self.parse_error(e, line))
        except Exception, e:
            raise MudderyError("%s (model: %s, line: %s)" % (e, self.model_name, line))

    def import_from_path(self, path_name, **kwargs):
        # import data from default position
        super(LocalizedStringsHandler, self).import_from_path(path_name, **kwargs)

        # import all files in LOCALIZED_STRINGS_FOLDER
        dir_name = os.path.join(path_name,
                                settings.LOCALIZED_STRINGS_FOLDER,
                                settings.LANGUAGE_CODE)

        if os.path.isdir(dir_name):
            # Does not clear previous data.
            kwargs["clear"] = False
            for file_name in os.listdir(dir_name):
                file_name = os.path.join(dir_name, file_name)
                if os.path.isdir(file_name):
                    # if it is a folder
                    continue

                self.import_file(file_name, **kwargs)

    def clear_model_data(self, **kwargs):
        """
        Remove all data from db.

        Args:
            model_name: (string) db model's name.

        Returns:
            None
        """
        system_data = kwargs.get('system_data', False)
        
        # clear old data
        self.objects.filter(system_data=system_data).delete()
