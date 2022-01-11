"""
This module imports data from files to db.
"""

import os, glob, tempfile, zipfile, shutil
import traceback

from muddery.server.conf import settings
from muddery.launcher.upgrader.upgrade_handler import UPGRADE_HANDLER
from muddery.launcher import configs
from muddery.launcher.utils import copy_tree
from muddery.worldeditor.database.db_manager import DBManager
from muddery.worldeditor.services.data_importer import import_file


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

        # load system localized strings
        # system data file's path
        system_data_path = os.path.join(settings.MUDDERY_DIR, settings.WORLD_DATA_FOLDER)

        # localized string file's path
        system_localized_string_path = os.path.join(system_data_path,
                                                    settings.LOCALIZED_STRINGS_FOLDER,
                                                    settings.LANGUAGE_CODE)

        # load data
        import_table_path(system_localized_string_path, settings.LOCALIZED_STRINGS_MODEL)

        # load custom localized strings
        # custom data file's path
        custom_localized_string_path = os.path.join(source_path, settings.LOCALIZED_STRINGS_MODEL)

        file_names = glob.glob(custom_localized_string_path + ".*")
        if file_names:
            print("Importing %s" % file_names[0])
            try:
                import_file(file_names[0], table_name=settings.LOCALIZED_STRINGS_MODEL, clear=False)
            except Exception as e:
                print("Import error: %s" % e)

    finally:
        shutil.rmtree(temp_path)


def unzip_resources_all(fp):
    """
    Import all resource files from a zip file.
    """
    media_dir = os.path.join(settings.MEDIA_ROOT, settings.IMAGE_PATH)
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


def import_data_path(path, clear=True, except_errors=False):
    """
    Import data from path.

    Args:
        path: (string) data path.
        clear: (boolean) clear old data.
        except_errors: (boolean) except error records and load other records.
    """
    # import tables one by one
    tables = DBManager.inst().get_tables(settings.WORLD_DATA_APP)
    for table_name in tables:
        file_names = glob.glob(os.path.join(path, table_name) + ".*")

        if file_names:
            print("Importing %s" % file_names[0])
            try:
                import_file(file_names[0], table_name=table_name, clear=clear, except_errors=except_errors)
            except Exception as e:
                traceback.print_exc()
                print("Import error: %s" % e)


def import_table_path(path, table_name, clear=True, except_errors=False):
    """
    Import a table's data from a path.

    Args:
        path: (string) data path.
        table_name: (string) table's name.
        clear: (boolean) clear old data.
        except_errors: (boolean) except error records and load other records.
    """
    if clear:
        DBManager.inst().clear_table(settings.WORLD_DATA_APP, table_name)

    if not os.path.isdir(path):
        return

    for file_name in os.listdir(path):
        file_name = os.path.join(path, file_name)
        if os.path.isdir(file_name):
            # if it is a folder
            continue

        print("Importing %s" % file_name)
        try:
            import_file(file_name, table_name=table_name, clear=False, except_errors=except_errors)
        except Exception as e:
            print("Import error: %s" % e)
