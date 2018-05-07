"""
This module imports data from files to db.
"""

from __future__ import print_function

import os
import tempfile
import zipfile
import shutil
from django.conf import settings
from evennia.utils import logger
from muddery.server.upgrader.upgrade_handler import UPGRADE_HANDLER
from muddery.server.launcher import configs
from muddery.server.launcher.utils import copy_tree
from muddery.utils import readers
from muddery.utils.exception import MudderyError, ERR
from muddery.worlddata.dao.data_importer import DataImporter


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

        # import models one by one
        data_handlers = DATA_SETS.all_handlers
        for data_handler in data_handlers:
            data_handler.import_from_path(source_path, system_data=False)

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


def import_data_file(fp, table_name=None):
    """
    Import a single data file.
    """
    data_importer = DataImporter()
    data_importer.import_file(fp, table_name=table_name)
    

