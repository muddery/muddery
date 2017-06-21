"""
General helper functions that don't fit neatly under any given category.

They provide some useful string and conversion methods that might
be of use when designing your own game.

"""

import os
import shutil
from datetime import datetime
from evennia.server import evennia_launcher
from muddery.server.launcher import utils as launcher_utils


def compare_version(ver1, ver2):
    """
    Compare two version.

    Args:
        ver1: (tuple) version number's list 1.
        ver2: (tuple) version number's list 2.

    Returns:
        -1: ver1 < ver2
        0: ver1 == ver2
        1: ver1 > ver2
    """
    if not ver1 or not ver2:
        return 0
    if ver1[0] < ver2[0]:
        return -1
    if ver1[0] > ver2[0]:
        return 1
    return compare_version(ver1[1:], ver2[1:])


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


def get_temp_dir_name(game_dir):
    """
    Move game dir to temp dir.
    """
    base_temp_dir = game_dir + "_temp_" + datetime.now().date().isoformat()
    temp_dir = base_temp_dir
    count = 1
    while os.path.exists(temp_dir):
        temp_dir = "%s(%s)" % (base_temp_dir, count)
        count += 1

    return temp_dir


def create_game(game_dir, game_template, setting_dict):
    """
    Create a new game dir.

    Args:
        game_dir: (string)game's dir

    Returns:
        None
    """
    launcher_utils.create_game_directory(game_dir, game_template, setting_dict)

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


def comment_out_class(file_path, class_name):
    """
    Comment out specified class in the file.

    Args:
        file_path: (string) file's path
        class_name: (string) the name of the class to comment out

    Returns:
        None
    """
    lines = []
    with open(file_path, "r") as f:
        lines = f.readlines()

    first_line = True
    comment_out = False
    for i, line in enumerate(lines):
        if line[:5] == "class" and class_name in line:
            comment_out = True

        if comment_out:
            if len(line.strip()) > 0:
                lines[i] = "# " + line

            if not first_line and line[0] != " ":
                break

            first_line = False

    with open(file_path, "w+") as f:
        f.writelines(lines)


def comment_out_lines(file_path, comment_lines):
    """
    Comment out specified class in the file.

    Args:
        file_path: (string) file's path
        comment_lines: (set) lines to append

    Returns:
        None
    """
    lines = []
    with open(file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip() in comment_lines:
            lines[i] = "# " + line

    with open(file_path, "w+") as f:
        f.writelines(lines)


def file_append(file_path, lines):
    """
    Append lines to the file.

    Args:
        file_path: (string) file's path
        lines: (list) lines to append

    Returns:
        None
    """
    with open(file_path, "a") as f:
        f.writelines(lines)
