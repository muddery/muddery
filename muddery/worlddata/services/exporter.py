"""
This module imports data from files to db.
"""

from __future__ import print_function

import os
import tempfile
import zipfile
from django.conf import settings
from evennia.utils import logger
from evennia.settings_default import GAME_DIR
from muddery.server.launcher import configs
from muddery.utils.exception import MudderyError, ERR
from muddery.utils import writers
from muddery.worlddata.dao import general_query_mapper, model_mapper


def export_file(filename, table_name, file_type=None):
    """
    Export a table to a csv file.
    """
    if not file_type:
        # Get file's extension name.
        file_type = os.path.splitext(filename)[1].lower()
        if len(file_type) > 0:
            file_type = file_type[1:]

    writer_class = writers.get_writer(file_type)
    if not writer_class:
        raise(MudderyError(ERR.export_data_error, "Unsupport file type %s" % file_type))

    writer = writer_class(filename)
    if not writer:
        raise(MudderyError(ERR.export_data_error, "Can not export table %s" % table_name))

    fields = general_query_mapper.get_all_fields(table_name)
    header = [field.name for field in fields]
    writer.writeln(header)

    records = general_query_mapper.get_all_records(table_name)
    for record in records:
        line = [str(record.serializable_value(field.get_attname())) for field in fields]
        writer.writeln(line)

    writer.save()


def export_zip_all(file_obj, file_type=None):
    """
    Export all tables to a zip file which contains a group of csv files.
    """
    if not file_type:
        # Set default file type.
        file_type = "csv"

    writer_class = writers.get_writer(file_type)
    if not writer_class:
        raise(MudderyError(ERR.export_data_error, "Unsupport file type %s" % file_type))

    # Get tempfile's name.
    temp = tempfile.mktemp()
    file_ext = writer_class.file_ext

    try:
        archive = zipfile.ZipFile(file_obj, 'w', zipfile.ZIP_DEFLATED)

        # get model names
        models = model_mapper.get_all_models()
        for model in models:
            model_name = model._meta.object_name
            export_file(temp, model_name, file_type)
            filename = model_name + "." + file_ext
            archive.write(temp, filename)

        # add version file
        version_file = os.path.join(GAME_DIR, configs.CONFIG_FILE)
        archive.write(version_file, configs.CONFIG_FILE)
    finally:
        os.remove(temp)


def export_resources(file_obj):
    """
    Export all resource files to a zip file.
    """
    dir_name = settings.MEDIA_ROOT
    dir_length = len(dir_name)

    archive = zipfile.ZipFile(file_obj, 'w', zipfile.ZIP_DEFLATED)   
    for root, dirs, files in os.walk(dir_name):
        for filename in files:
            if filename[:1] == '.':
                continue

            full_path = os.path.join(root, filename)
            file_name = full_path[dir_length:]
            archive.write(full_path, file_name)
