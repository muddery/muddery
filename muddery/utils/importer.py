"""
This module imports data from files to db.
"""

from __future__ import print_function

import os
import glob
import tempfile
import zipfile
import shutil
from django.db import models
from django.apps import apps
from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.utils import readers
from muddery.worlddata.data_handler import SYSTEM_DATA_HANDLER, DATA_HANDLER


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
        field_type = 0

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
            logger.log_errmsg("Field error: %s" % e)

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
            if field_type == 0:
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
            print("value error: %s - '%s'" % (field_name, value))
            
    return record


def import_data(model_obj, reader, system_data):
    """
    Import data to the model.

    Args:
        model_obj:
        reader:

    Returns:
        None
    """
    try:
        # read title
        titles = reader.readln()

        field_types = get_field_types(model_obj, titles)

        found_key = False
        key_index = 0
        if system_data:
            # get pk's position
            for index, title in enumerate(titles):
                if title == "key":
                    found_key = True
                    key_index = index
                    break
            if not found_key:
                print("Can not found system data's key.")
                return

        # import values
        # read next line
        values = reader.readln()

        while values:
            try:
                record = parse_record(titles, field_types, values)

                # Merge system and custom data.
                if system_data:
                    # System data can not overwrite custom data.
                    if model_obj.objects.filter(key=values[key_index], system_data=False).count() > 0:
                        continue

                    # Add system data flag.
                    record["system_data"] = True

                data = model_obj(**record)
                data.save()
            except Exception, e:
                print("Can not load %s: %s" % (values, e))

            # read next line
            values = reader.readln()

    except StopIteration:
        # reach the end of file, pass this exception
        pass


def import_file(file_name, model_name, file_type=None, wildcard=True, system_data=False):
    """
    Import data from a data file to the db model

    Args:
        file_name: (string) file's name
        model_name: (string) db model's name.
        file_type: (string) the type of the file. If it's None, the function will get
                   the file type from the extension name of the file.
        wildcard: (bool) add wildcard as ext name or not.
        system_data: (bool) is system data or not.
    """
    imported = False

    try:
        # get file list
        if wildcard:
            file_names = glob.glob(file_name + ".*")
        else:
            file_names = [file_name]

        for file_name in file_names:
            if not file_type:
                # get file's extension name
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

            # get model
            model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)

            print()
            print("Importing %s" % file_name)
            import_data(model_obj, reader, system_data)
            imported = True
            break
    except Exception, e:
        print("Can not import file %s: %s" % (file_name, e))

    if imported:
        print("%s imported." % file_name)
    else:
        print("Can not import file %s" % file_name)

    return imported


def import_local_all():
    """
    Import all local data files to models.
    """
    ##########################
    # load system data
    ##########################
    # system data file's path
    system_data_path = os.path.join(settings.MUDDERY_DIR, settings.WORLD_DATA_FOLDER)

    # load models in order
    model_list = SYSTEM_DATA_HANDLER.SystemData.all()

    # import models one by one
    for model_name in model_list:
        clear_model_data(model_name, is_system_model=True, system_data=True)
        file_name = os.path.join(system_data_path, model_name)
        import_file(file_name, model_name, system_data=True)

    ##########################
    # load custom data
    ##########################
    # custom data file's path
    custom_data_path = os.path.join(settings.GAME_DIR, settings.WORLD_DATA_FOLDER)

    # load system models
    model_list = DATA_HANDLER.SystemData.all()

    # import models one by one
    for model_name in model_list:
        clear_model_data(model_name, is_system_model=True, system_data=False)
        file_name = os.path.join(custom_data_path, model_name)
        import_file(file_name, model_name, system_data=False)

    # load models in order
    model_list = []
    model_list.extend(DATA_HANDLER.BasicData.all())
    model_list.extend(DATA_HANDLER.ObjectsData.all())
    model_list.extend(DATA_HANDLER.ObjectsAdditionalData.all())
    model_list.extend(DATA_HANDLER.OtherData.all())
    model_list.extend(DATA_HANDLER.EventAdditionalData.all())

    # import models one by one
    for model_name in model_list:
        clear_model_data(model_name, is_system_model=False, system_data=False)
        file_name = os.path.join(custom_data_path, model_name)
        import_file(file_name, model_name, system_data=False)


def clear_model_data(model_name, is_system_model, system_data):
    """
    Remove all data from db.

    Args:
        model_name: (string) db model's name.
        is_system_model: (bool) is systm data model or not.
        system_data: (bool) remove system data or custom data.

    Returns:
        None
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)

    # clear old data
    if is_system_model:
        model_obj.objects.filter(system_data=system_data).delete()
    else:
        model_obj.objects.all().delete()


def unzip_data_all(file):
    """
    Import all data files from a zip file.
    """
    temp_path = tempfile.mkdtemp()

    try:
        archive = zipfile.ZipFile(file, 'r')
        archive.extractall(temp_path)

        # import models one by one
        # load system models
        model_list = DATA_HANDLER.SystemData.all()

        for model_name in model_list:
            clear_model_data(model_name, is_system_model=True, system_data=False)
            file_name = os.path.join(temp_path, model_name)
            import_file(file_name, model_name, system_data=False)

        # import models
        model_list = []
        model_list.extend(DATA_HANDLER.BasicData.all())
        model_list.extend(DATA_HANDLER.ObjectsData.all())
        model_list.extend(DATA_HANDLER.ObjectsAdditionalData.all())
        model_list.extend(DATA_HANDLER.OtherData.all())
        model_list.extend(DATA_HANDLER.EventAdditionalData.all())

        # import models one by one
        for model_name in model_list:
            clear_model_data(model_name, is_system_model=False, system_data=False)
            file_name = os.path.join(temp_path, model_name)
            import_file(file_name, model_name, system_data=False)
    finally:
        shutil.rmtree(temp_path)


def unzip_resources_all(file):
    """
    Import all resource files from a zip file.
    """
    media_dir = settings.MEDIA_ROOT
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    archive = zipfile.ZipFile(file)
    for name in archive.namelist():
        if os.path.isdir(name):
            os.makedirs(os.path.join(media_dir, name))
        else:            
            filename = os.path.join(media_dir, name)
            dir_name = os.path.dirname(filename)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            outfile = open(filename, 'wb')
            outfile.write(archive.read(name))
            outfile.close()
