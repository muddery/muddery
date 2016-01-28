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
    """
    csvfile = open(file_name, 'w')
    writer = csv.writer(csvfile)

    for line in get_lines(model_name):
        writer.writerow(line)


def export_zip_all(file):
    """
    """
    archive = zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED)
    temp = tempfile.mktemp()

    # get model names
    appconfig = apps.get_app_config(settings.WORLD_DATA_APP)
    for model in appconfig.get_models():
        name = model._meta.object_name
        export_file(temp, name)
        archive.write(temp, name + ".csv")

    archive.close()
    os.remove(temp)


def export_all(path_name):
    """
    Import all data files to models.
    """
    # get model names
    appconfig = apps.get_app_config(settings.WORLD_DATA_APP)
    for model in appconfig.get_models():
        name = model._meta.verbose_name
        export_file(path_name + name, name)
