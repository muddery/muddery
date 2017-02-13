"""
This module imports data from files to db.
"""

from __future__ import print_function

import os
import csv
import tempfile
import zipfile
from django.apps import apps
from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.utils import readers


def get_header(model_name):
    """
    Get a model's header.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
    return model_obj._meta.fields


def get_lines(model_name):
    """
    Import data from a data file to the db model

    Args:
        file_name: (string) file's name
        model_name: (string) db model's name.
    """
    # get model
    model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
    fields = model_obj._meta.fields
    yield [field.name for field in fields]

    # get records
    for record in model_obj.objects.all():
        line = [record.serializable_value(field.name) for field in fields]
        yield line


def export_file(file_name, model_name):
    """
    Export a table to a csv file.
    """
    csv_file = open(file_name, 'w')
    writer = csv.writer(csv_file)

    for line in get_lines(model_name):
        writer.writerow(line)

    csv_file.close()


def export_zip_all(file):
    """
    Export all tables to a zip file which contains a group of csv files.
    """
    temp = tempfile.mktemp()

    try:
        archive = zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED)

        # get model names
        app_config = apps.get_app_config(settings.WORLD_DATA_APP)
        for model in app_config.get_models():
            model_name = model._meta.object_name
            export_file(temp, model_name)
            filename = model_name + ".csv"
            archive.write(temp, filename)
    finally:
        os.remove(temp)


def export_all(path_name):
    """
    Export all data files from models.
    """
    # get model names
    app_config = apps.get_app_config(settings.WORLD_DATA_APP)
    for model in app_config.get_models():
        name = model._meta.verbose_name
        export_file(path_name + name, name)


def export_resources(file):
    """
    Export all resource files to a zip file.
    """
    dir_name = settings.MEDIA_ROOT
    dir_length = len(dir_name)

    archive = zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED)   
    for root, dirs, files in os.walk(dir_name):
        for file in files:
            if file[:1] == '.':
                continue

            full_path = os.path.join(root, file)
            file_name = full_path[dir_length:]
            archive.write(full_path, file_name)
