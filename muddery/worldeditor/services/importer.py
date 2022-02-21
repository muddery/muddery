
import os, tempfile, zipfile, shutil
import traceback
from muddery.launcher.upgrader.upgrade_handler import UPGRADE_HANDLER
from muddery.launcher import configs
from muddery.launcher.utils import copy_tree
from muddery.server.settings import SETTINGS
from muddery.server.utils.importer import import_data_path, import_table_path


def unzip_data_all(fp):
    """
    Import all data files from a zip file.
    """
    with tempfile.TemporaryDirectory() as temp_path:
        archive = zipfile.ZipFile(fp, 'r')
        archive.extractall(temp_path)
        source_path = temp_path

        # if the zip file contains a root dir
        file_list = os.listdir(temp_path)
        if len(file_list) == 1:
            path = os.path.join(temp_path, file_list[0])
            if os.path.isdir(path):
                source_path = path

        # import data from path
        import_data_path(source_path)

        # load system localized strings
        # system data file's path
        system_data_path = os.path.join(SETTINGS.MUDDERY_DIR, SETTINGS.WORLD_DATA_FOLDER)

        # localized string file's path
        system_localized_string_path = os.path.join(system_data_path,
                                                    SETTINGS.LOCALIZED_STRINGS_FOLDER,
                                                    SETTINGS.LANGUAGE_CODE)

        # load data
        import_table_path(system_localized_string_path, SETTINGS.LOCALIZED_STRINGS_MODEL)

        # load custom localized strings
        # custom data file's path
        custom_localized_string_path = os.path.join(source_path, SETTINGS.LOCALIZED_STRINGS_MODEL)

        # load data
        import_table_path(custom_localized_string_path, SETTINGS.LOCALIZED_STRINGS_MODEL)


def unzip_resources_all(fp):
    """
    Import all resource files from a zip file.
    """
    media_dir = os.path.join(SETTINGS.MEDIA_ROOT, SETTINGS.IMAGE_PATH)
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    with tempfile.TemporaryDirectory() as temp_path:
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
