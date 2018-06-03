"""
This module imports data from files to db.
"""

from __future__ import print_function

import os, glob, tempfile, zipfile, shutil
from django.conf import settings
from evennia.utils import logger
from muddery.server.upgrader.upgrade_handler import UPGRADE_HANDLER
from muddery.server.launcher import configs
from muddery.server.launcher.utils import copy_tree
from muddery.utils import readers
from muddery.utils.exception import MudderyError, ERR
from muddery.worlddata.dao.data_importer import import_file
from muddery.worlddata.dao import model_mapper


def unzip_data_all(fp):
    """
    Import all data files from a zip file.
    """
    temp_path = tempfile.mkdtemp()

    try:
        archive = zipfile.ZipFile(fp, 'r')
        archive.extractall(temp_path)
        source_path = temp_path
        
        # if the zip file contains a root dir
        file_list = os.listdir(temp_path)
        if len(file_list) == 1:
            path = os.path.join(temp_path, file_list[0])
            if os.path.isdir(path):
                source_path = path

        # Upgrade game data.
        UPGRADE_HANDLER.upgrade_data(source_path, None, configs.MUDDERY_LIB)

        # import data from path
        import_data_path(source_path)

    finally:
        shutil.rmtree(temp_path)


def unzip_resources_all(fp):
    """
    Import all resource files from a zip file.
    """
    media_dir = settings.MEDIA_ROOT
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    temp_path = tempfile.mkdtemp()

    try:
        archive = zipfile.ZipFile(fp, 'r')
        archive.extractall(temp_path)
        source_path = temp_path
        
        # if the zip file contains a root dir
        file_list = os.listdir(temp_path)
        if len(file_list) == 1:
            path = os.path.join(temp_path, file_list[0])
            if os.path.isdir(path):
                source_path = path

        copy_tree(source_path, media_dir)

    finally:
        shutil.rmtree(temp_path)


def import_data_path(path, clear=True):
    """
    Import data from path.

    Args:
        path: (string) data path.
    """

    # import tables one by one
    models = model_mapper.get_all_models()
    for model in models:
        table_name = model.__name__
        file_names = glob.glob(os.path.join(path, table_name) + ".*")

        if file_names:
            print("Importing %s" % file_names[0])
            try:
                import_file(file_names[0], table_name=table_name, clear=clear)
            except Exception, e:
                print("Import error: %s" % e)


def import_data_file(fp, table_name=None, file_type=None, clear=True):
    """
    Import a single data file.
    """
    fp.flush()
    import_file(fp.name, table_name=table_name, file_type=file_type, clear=clear)


def import_table_path(path, table_name, clear=True):
    """
    Import a table's data from a path.
    """
    # clear old data
    model = model_mapper.get_model(table_name)
    if not model:
        return

    if clear:
        model.objects.all().delete()

    if not os.path.isdir(path):
        return

    for file_name in os.listdir(path):
        file_name = os.path.join(path, file_name)
        if os.path.isdir(file_name):
            # if it is a folder
            continue

        print("Importing %s" % file_name)
        try:
            import_file(file_name, table_name=table_name, clear=False)
        except Exception, e:
            print("Import error: %s" % e)
