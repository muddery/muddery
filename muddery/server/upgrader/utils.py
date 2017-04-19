"""
General helper functions that don't fit neatly under any given category.

They provide some useful string and conversion methods that might
be of use when designing your own game.

"""

import os
import shutil
from datetime import datetime
from evennia.server import evennia_launcher
from muddery.server import muddery_launcher


def get_data_version(path):
    """
    Transform a vesion string to version and sub version numbers.

    Args:
        path: (string) the path of the game or data.

    Returns:
        (tuple): data's version number list.
    """
    game_ver = ""
    try:
        with open(os.path.join(path, "muddery_version.txt"), 'r') as f:
            game_ver = f.read().strip()
    except Exception, e:
        pass

    ver_list = game_ver.split('.')
    num_list = [0, 0]
    for i, ver in enumerate(ver_list):
        if i >= len(num_list):
            break
        if ver:
            num_list[i] = int(ver)

    return tuple(num_list)


def make_backup(game_dir):
    """
    Backup game dir.
    """
    # back up to a new dir
    base_backup_dir = game_dir + "_bak_" + datetime.now().date().isoformat()
    backup_dir = base_backup_dir
    count = 1
    while os.path.exists(backup_dir):
        backup_dir = "%s(%s)" % (base_backup_dir, count)
        count += 1

    # copy game dir to backup dir
    try:
        copy_tree(game_dir, backup_dir)
    except Exception, e:
        print("Can not create backup dir: %s" % e)
        raise(Exception)


def to_temp_dir(game_dir):
    """
    Move game dir to temp dir.
    """
    base_temp_dir = game_dir + "_temp_" + datetime.now().date().isoformat()
    temp_dir = base_temp_dir
    count = 1
    while os.path.exists(temp_dir):
        temp_dir = "%s(%s)" % (base_temp_dir, count)
        count += 1

    os.rename(game_dir, temp_dir)

    return temp_dir


def create_game(game_dir, game_template, setting_dict):
    """
    Create a new game dir.

    Args:
        game_dir: (string)game's dir

    Returns:
        None
    """
    muddery_launcher.create_game_directory(game_dir, game_template, setting_dict)

    os.chdir(game_dir)
    evennia_launcher.init_game_directory(game_dir, check_db=False)


def copy_path(src_dir, dest_dir, path):
    """
    Copy a file from the source dir to the destination dir.

    Args:
        src_dir:
        dest_dir:
        path:

    Returns:
        None
    """
    src_path = os.path.join(src_dir, path)
    dest_path = os.path.join(dest_dir, path)

    if os.path.isdir(src_path):
        copy_tree(src_path, dest_path)
    else:
        shutil.copy2(src_path, dest_path)


def copy_tree(source, destination):
    """
    copy file tree
    """
    if not os.path.exists(destination):
        # If does not exist, create one.
        os.mkdir(destination)

    # traverse files and folders
    names = os.listdir(source)
    for name in names:
        srcname = os.path.join(source, name)
        dstname = os.path.join(destination, name)
        try:
            if os.path.isdir(srcname):
                # If it is a folder, copy it recursively.
                copy_tree(srcname, dstname)
            else:
                # Copy file.
                shutil.copy2(srcname, dstname)
        except Exception, e:
            print("Can not copy file:%s to %s for %s." % (srcname, dstname, e))
            raise(Exception)


def get_settings(game_dir, setting_list):
    """
    Get values in setting dict from settings file.
    """
    setting_dict = {}
    settings_path = os.path.join(game_dir, "server", "conf", "settings.py")
    with open(settings_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            contents = line.split("=")
            if len(contents) == 2:
                key = contents[0].strip()
                if key in setting_list:
                    setting_dict[key] = contents[1].strip()
    return setting_dict
