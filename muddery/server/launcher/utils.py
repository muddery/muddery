#!/usr/bin/env python
"""

"""

from __future__ import print_function

import os
import sys
import shutil
import ConfigParser
from subprocess import check_output, CalledProcessError, STDOUT
from evennia.server import evennia_launcher
from muddery.server.launcher import configs

#------------------------------------------------------------
#
# Functions
#
#------------------------------------------------------------

def muddery_version():
    """
    Get the Muddery version info from the main package.
    """
    version = "Unknown"
    try:
        import muddery
        version = muddery.__version__
    except ImportError:
        pass
    try:
        rev = check_output("git rev-parse --short HEAD", shell=True, cwd=configs.MUDDERY_ROOT, stderr=STDOUT).strip()
        version = "%s (rev %s)" % (version, rev)
    except (IOError, CalledProcessError):
        pass
    return version


def short_version():
    """
    Get the short Muddery version.
    """
    version = "Unknown"
    try:
        import muddery
        version = muddery.__version__
    except ImportError:
        pass
    return version

SHORT_VERSION = short_version()


def create_secret_key():
    """
    Randomly create the secret key for the settings file
    """
    import random
    import string
    secret_key = list((string.letters +
                       string.digits +
                       string.punctuation).replace("\\", "").replace("'", '"'))
    random.shuffle(secret_key)
    secret_key = "".join(secret_key[:40])
    return secret_key


def create_settings_file(setting_dict=None):
    """
    Uses the template settings file to build a working
    settings file.

    Args:
        setting_dict: (dict)preset settings.
    """
    settings_path = os.path.join(GAME_DIR, "server", "conf", "settings.py")
    with open(settings_path, 'r') as f:
        settings_string = f.read()

    # tweak the settings
    default_setting_dict = {"EVENNIA_SETTINGS_DEFAULT": os.path.join(evennia_launcher.EVENNIA_LIB, "settings_default.py"),
                            "MUDDERY_SETTINGS_DEFAULT": os.path.join(configs.MUDDERY_LIB, "settings_default.py"),
                            "ALLOWED_HOSTS": "['*']",
                            "WEBSERVER_PORTS": "[(8000, 5001)]",
                            "WEBSOCKET_CLIENT_PORT": "8001",
                            "AMP_PORT": "5000",
                            "LANGUAGE_CODE": "'en-us'",
                            "SECRET_KEY":"'%s'" % create_secret_key()}

    if setting_dict:
        merged_setting_dict = dict(default_setting_dict, **setting_dict)
    else:
        merged_setting_dict = default_setting_dict

    # modify the settings
    settings_string = settings_string.format(**merged_setting_dict)

    with open(settings_path, 'w') as f:
        f.write(settings_string)


def create_game_directory(gamedir, template, setting_dict=None):
    """
    Initialize a new game directory named dirname
    at the current path. This means copying the
    template directory from muddery's root.
    """
    
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


    global GAME_DIR
    GAME_DIR = gamedir
    if os.path.exists(GAME_DIR):
        print("Cannot create new Muddery game dir: '%s' already exists." % gamedir)
        sys.exit()

    template_dir = ""
    if template:
        template_dir = os.path.join(configs.MUDDERY_TEMPLATE, template)
        if not os.path.exists(template_dir):
            print('Sorry, template "%s" does not exist.\nThese are available templates:' % template)
            dirs = os.listdir(configs.MUDDERY_TEMPLATE)
            for dir in dirs:
                full_path = os.path.join(configs.MUDDERY_TEMPLATE, dir)
                if os.path.isdir(full_path):
                    print("  %s" % dir)
            print("")
            sys.exit()

    # copy default template directory
    default_template = os.path.join(configs.MUDDERY_LIB, configs.TEMPLATE_DIR)
    shutil.copytree(default_template, GAME_DIR)

    # write config file
    create_config_file(gamedir, template)

    if template_dir:
        copy_tree(template_dir, GAME_DIR)

    # pre-build settings file in the new GAME_DIR
    create_settings_file(setting_dict)


def show_version_info(about=False):
    """
    Display version info
    """
    import os, sys
    import twisted
    import django
    import evennia

    return configs.VERSION_INFO.format(version=muddery_version(),
                                       about=configs.ABOUT_INFO if about else "",
                                       os=os.name, python=sys.version.split()[0],
                                       twisted=twisted.version.short(),
                                       django=django.get_version(),
                                       evennia=evennia.__version__,)


def check_gamedir(path):
    """
    Check if the path is a game dir.
    """
    settings_path = os.path.join(path, "server", "conf", "settings.py")
    if os.path.isfile(settings_path):
        return

    print(configs.ERROR_NO_GAMEDIR)
    sys.exit()


def create_config_file(game_dir, template):
    """
    Create game's config file. Set version and template info.

    Args:
        game_dir: (String) game's dir name
        template: (String) game template's name

    Returns:
        None
    """
    config_file = open(os.path.join(game_dir, configs.CONFIG_FILE), "w")
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.add_section(configs.VERSION_SECTION)
    config_parser.set(configs.VERSION_SECTION, configs.VERSION_ITEM, SHORT_VERSION)
    if template:
        config_parser.set(configs.VERSION_SECTION, configs.TEMPLATE_ITEM, template)
    config_parser.write(config_file)
    config_file.close()


def get_game_config(path):
    """
    Get game's version and template.

    Args:
        path: (string) the path of the game or data.

    Returns:
        (tuple): version, template name
    """
    game_ver = ""
    game_template = ""

    # read game config file
    try:
        config_parser = ConfigParser.SafeConfigParser()
        config_parser.read(os.path.join(path, configs.CONFIG_FILE))
        game_ver = config_parser.get(configs.VERSION_SECTION, configs.VERSION_ITEM)
        game_template = config_parser.get(configs.VERSION_SECTION, configs.TEMPLATE_ITEM)
    except:
        pass

    if not game_ver:
        # read version text file
        try:
            with open(os.path.join(path, "muddery_version.txt"), 'r') as f:
                game_ver = f.read().strip()
        except:
            pass

    ver_list = game_ver.split('.')
    num_list = [0, 0, 0]
    for i, ver in enumerate(ver_list):
        if i >= len(num_list):
            break
        if ver:
            num_list[i] = int(ver)

    return tuple(num_list), game_template