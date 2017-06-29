"""
This module imports data from files to db.
"""

from __future__ import print_function

import os
import tempfile
import zipfile
import shutil
from django.conf import settings
from muddery.server.upgrader.upgrade_handler import UPGRADE_HANDLER
from muddery.server.launcher import configs
from muddery.worlddata.data_sets import DATA_SETS


def unzip_data_all(file):
    """
    Import all data files from a zip file.
    """
    temp_path = tempfile.mkdtemp()

    try:
        archive = zipfile.ZipFile(file, 'r')
        archive.extractall(temp_path)

        # Upgrade game data.
        UPGRADE_HANDLER.upgrade_data(temp_path, None, configs.MUDDERY_LIB)

        # import models one by one
        data_handlers = DATA_SETS.all_handlers
        for data_handler in data_handlers:
            data_handler.import_from_path(temp_path, system_data=False)

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
