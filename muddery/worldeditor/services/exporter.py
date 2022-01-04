"""
This module imports data from files to db.
"""

import os
import tempfile
import zipfile
from django.conf import settings
from muddery.launcher import configs
from muddery.server.utils.exception import MudderyError, ERR
from muddery.worldeditor.database.db_manager import DBManager
from muddery.worldeditor.utils import writers
from muddery.worldeditor.dao import general_querys


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

    fields = general_querys.get_field_names(table_name)
    writer.writeln(fields)

    records = general_querys.get_all_records(table_name)
    for record in records:
        line = [str(getattr(record, field)) for field in fields]
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
    temp_filename = tempfile.mktemp()
    file_ext = writer_class.file_ext

    try:
        archive = zipfile.ZipFile(file_obj, 'w', zipfile.ZIP_DEFLATED)

        # get model names
        models = DBManager.inst().get_tables(settings.WORLD_DATA_APP)
        for model in models:
            model_name = model._meta.object_name
            export_file(temp_filename, model_name, file_type)
            filename = model_name + "." + file_ext
            archive.write(temp_filename, filename)

        # add version file
        version_file = os.path.join(configs.GAME_DIR, configs.CONFIG_FILE)
        archive.write(version_file, configs.CONFIG_FILE)
    finally:
        try:
            os.remove(temp_filename)
        except PermissionError:
            pass


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
