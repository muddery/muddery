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


def import_file(file_name, model_name, widecard=True, clear=True):
    """
    Import data from a data file to the db model

    Args:
        file_name: (string) file's name
        model_name: (string) db model's name.
        widecard: (bool) add widecard as ext name or not.
        clear: (boolean) clear old data or not.
    """
    imported = False

    try:
        # get file list
        if widecard:
            file_names = glob.glob(file_name + ".*")
        else:
            file_names = [file_name]

        for file_name in file_names:
            # get file's extension name
            ext_name = os.path.splitext(file_name)[1].lower()

            reader = None
            if ext_name == ".csv":
                reader = readers.csv_reader(file_name)
            elif ext_name == ".xls" or ext_name == ".xlsx":
                reader = readers.xls_reader(file_name)

            if not reader:
                # does support this file type, read next one.
                continue

            imported = True

            # get model
            model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)

            if clear:
                # clear old data
                model_obj.objects.all().delete()

            try:
                # read title
                title = reader.next()

                # get field types
                # type = 0    means common field
                # type = 1    means Boolean field
                # type = 2    means Integer field
                # type = 3    means Float field
                # type = 4    means ForeignKey field, not support
                # type = 5    means ManyToManyField field, not support
                # type = -1   means field does not exist

                field_types = []
                for field_name in title:
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

                # import values
                # read next line
                values = reader.next()

                while values:
                    try:
                        record = {}
                        for item in zip(title, field_types, values):
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

                        # create new record
                        data = model_obj.objects.create(**record)
                        data.save()
                    except Exception, e:
                        print("Can not load %s %s: %s" % (file_name, values, e))

                    # read next line
                    values = reader.next()

            except StopIteration:
                # reach the end of file, pass this exception
                pass

            break
    except Exception, e:
        print("Can not import file %s: %s" % (file_name, e))

    if imported:
        print("%s imported." % file_name)
    else:
        print("Can not import file %s" % file_name)


def import_model(model_name, path_name=None, clear=True):
    """
    Import data from a data file to the db model

    Args:
        model_name: (string) db model's name.
        clear: (boolean) clear old data or not.
    """
    if not path_name:
        path_name = os.path.join(settings.GAME_DIR, settings.WORLD_DATA_FOLDER)
    file_name = os.path.join(path_name, model_name)
    import_file(file_name, model_name, widecard=True, clear=clear)


def import_localized_strings(language=None):
    """
    Import localized strings.

    language: All choices can be found here: 
              # http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
    """
    # if language is empty, load settings.LANGUAGE_CODE
    if not language:
        language = settings.LANGUAGE_CODE

    # import all files in LANGUAGE_FOLDER
    dir_name = os.path.join(settings.GAME_DIR,
                            settings.WORLD_DATA_FOLDER,
                            settings.LOCALIZED_STRINGS_FOLDER,
                            language)

    if os.path.isdir(dir_name):
        for file_name in os.listdir(dir_name):
            full_name = os.path.join(dir_name, file_name)

            if os.path.isdir(full_name):
                # if it is a folder
                continue

            import_file(full_name, settings.LOCALIZED_STRINGS_MODEL, widecard=False, clear=False)


def import_zip_all(file):
    """
    Import all data files from a zip file.
    """
    temp = tempfile.mkdtemp()

    try:
        archive = zipfile.ZipFile(file, 'r')
        archive.extractall(temp)

        # import models
        model_name_list = settings.BASIC_DATA_MODELS +\
                          settings.OBJECT_DATA_MODELS +\
                          settings.OTHER_DATA_MODELS +\
                          (settings.LOCALIZED_STRINGS_MODEL,)

        # import models one by one
        for model_name in model_name_list:
            import_model(model_name, path_name=temp)
    finally:
        shutil.rmtree(temp)


def import_local_all():
    """
    Import all local data files to models.
    """
    # load models in order
    model_name_list = settings.BASIC_DATA_MODELS + settings.OBJECT_DATA_MODELS + settings.OTHER_DATA_MODELS

    # import models one by one
    for model_name in model_name_list:
        import_model(model_name)

    # import localized strings
    import_localized_strings(settings.LANGUAGE_CODE)


def import_resources(file):
    """
    Import all resource files from a zip file.
    """
    dir_name = settings.MEDIA_ROOT
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    archive = zipfile.ZipFile(file)
    for name in archive.namelist():
        if name.endswith('/'):
            os.makedirs(os.path.join(dir_name, name))
        else:            
            filename = os.path.join(dir_name, name)
            dir = os.path.dirname(filename)
            if not os.path.exists(dir):
                os.makedirs(dir)

            outfile = open(filename, 'wb')
            outfile.write(archive.read(name))
            outfile.close()