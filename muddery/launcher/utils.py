#!/usr/bin/env python
"""

"""

import os
import sys
import shutil
import configparser
import traceback
from pathlib import Path
from subprocess import check_output, CalledProcessError, STDOUT
import django.core.management
from muddery.launcher import configs

# ------------------------------------------------------------
#
# Functions
#
# ------------------------------------------------------------


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
        version = "%s (rev %s)" % (version, rev.decode())
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
    secret_key = list((string.ascii_letters +
                       string.digits + string.punctuation).replace("\\", "")
                      .replace("'", '"').replace("{", "_").replace("}", "-"))
    random.shuffle(secret_key)
    secret_key = "".join(secret_key[:40])
    return secret_key


def create_server_settings_file(gamedir, setting_dict=None):
    """
    Uses the template settings file to build a working
    settings file.

    Args:
        gamedir: (string) game root's path
        setting_dict: (dict)preset settings.
    """
    settings_path = os.path.join(gamedir, "server", "conf", "settings.py")
    with open(settings_path, 'r') as f:
        settings_string = f.read()

    # tweak the settings
    muddery_settings_file = Path(os.path.join(configs.MUDDERY_LIB, "settings_default.py")).as_posix()
    default_setting_dict = {"MUDDERY_SETTINGS_DEFAULT": muddery_settings_file,
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


def create_editor_settings_file(gamedir, setting_dict=None):
    """
    Uses the template settings file to build a working
    settings file.

    Args:
        gamedir: (string) game root's path
        setting_dict: (dict)preset settings.
    """
    settings_path = os.path.join(gamedir, "worldeditor", "conf", "settings.py")
    with open(settings_path, 'r') as f:
        settings_string = f.read()

    # tweak the settings
    muddery_settings_file = Path(os.path.join(configs.MUDDERY_LIB, "worldeditor", "settings_default.py")).as_posix()
    default_setting_dict = {"MUDDERY_SETTINGS_DEFAULT": muddery_settings_file,
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


def create_webclient_settings(gamedir, setting_dict=None):
    """
    Uses the template settings file to build a working
    webclient settings file.

    Args:
        gamedir: (string) game root's path
        setting_dict: (dict)preset settings.
    """
    settings_path = os.path.join(gamedir, "web", "webclient_overrides", "webclient", "settings.js")
    with open(settings_path, 'r') as f:
        settings_string = f.read()

    # tweak the settings
    default_setting_dict = {
        "WEBSOCKET_HOST": "'ws://' + window.location.hostname + ':8001'",
        "RESOURCE_HOST": "window.location.protocol + '//' + window.location.host + '/media/'",
    }

    if setting_dict:
        merged_setting_dict = dict(default_setting_dict, **setting_dict)
    else:
        merged_setting_dict = default_setting_dict

    # modify the settings
    settings_string = settings_string.format(**merged_setting_dict)

    with open(settings_path, 'w') as f:
        f.write(settings_string)


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
        except Exception as e:
            print("Can not copy file:%s to %s for %s." % (srcname, dstname, e))
                

def create_game_directory(gamedir, template, port=None):
    """
    Initialize a new game directory named dirname
    at the current path. This means copying the
    template directory from muddery's root.
    """
    if os.path.exists(gamedir):
        raise Exception("Cannot create new Muddery game dir: '%s' already exists." % gamedir)

    template_dir = ""
    if template:
        template_dir = os.path.join(configs.GAME_TEMPLATES, template)
        if not os.path.exists(template_dir):
            print('Sorry, template "%s" does not exist.\nThese are available templates:' % template)
            dirs = os.listdir(configs.GAME_TEMPLATES)
            for dir in dirs:
                full_path = os.path.join(configs.GAME_TEMPLATES, dir)
                if os.path.isdir(full_path):
                    print("  %s" % dir)
            print("")
            raise Exception()

    # copy default template directory
    default_template = os.path.join(configs.GAME_TEMPLATES, configs.DEFAULT_TEMPLATE)
    shutil.copytree(default_template, gamedir)

    # write config file
    create_config_file(gamedir, template)

    if template_dir:
        copy_tree(template_dir, gamedir)

    # pre-build settings file in the new gamedir
    setting_py_dict = None
    if port:
        setting_py_dict = {
            "WEBSERVER_PORTS": "[(%s, %s)]" % (port, port + 3),
            "WEBSOCKET_CLIENT_PORT": "%s" % (port + 1),
            "AMP_PORT": "%s" % (port + 2),
        }

    create_server_settings_file(gamedir, setting_py_dict)
    create_editor_settings_file(gamedir, setting_py_dict)

    setting_js_dict = None
    if port:
        setting_js_dict = {
            "WEBSOCKET_HOST": "'ws://' + window.location.hostname + ':%s'" % (port + 1),
        }
    create_webclient_settings(gamedir, setting_js_dict)


def show_version_info(about=False):
    """
    Display version info
    """
    import os, sys
    import django

    return configs.VERSION_INFO.format(version=muddery_version(),
                                       about=configs.ABOUT_INFO if about else "",
                                       os=os.name, python=sys.version.split()[0],
                                       django=django.get_version())


def check_gamedir(path):
    """
    Check if the path is a game dir.
    """
    settings_path = os.path.join(path, "server", "conf", "settings.py")
    if os.path.isfile(settings_path):
        return True

    print(configs.ERROR_NO_GAMEDIR)
    return False


def check_version():
    # check current game's version
    if not check_gamedir(configs.CURRENT_DIR):
        return False

    from muddery.launcher.upgrader.upgrade_handler import UPGRADE_HANDLER
    game_ver, game_template = get_game_config(configs.CURRENT_DIR)
    if UPGRADE_HANDLER.can_upgrade(game_ver):
        return False

    return True


def check_database():
    """
    Check so the database exists.

    Returns:
        exists (bool): `True` if the database exists, otherwise `False`.
    """
    # Check so a database exists and is accessible
    from django.db import connection

    tables = connection.introspection.get_table_list(connection.cursor())
    if not tables or not isinstance(tables[0], str):  # django 1.8+
        tables = [tableinfo.name for tableinfo in tables]
    return tables and "accounts_accountdb" in tables


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
    config_parser = configparser.ConfigParser()
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
        config_parser = configparser.ConfigParser()
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


def import_local_data(clear=False):
    """
    Import all local data files to models.
    """
    from django.conf import settings
    from muddery.worldeditor.services import importer

    # load custom data
    # data file's path
    data_path = os.path.join(settings.GAME_DIR, settings.WORLD_DATA_FOLDER)
    importer.import_data_path(data_path, clear=clear, except_errors=True)

    # localized string file's path
    localized_string_path = os.path.join(data_path, settings.LOCALIZED_STRINGS_FOLDER, settings.LANGUAGE_CODE)
    importer.import_table_path(localized_string_path, settings.LOCALIZED_STRINGS_MODEL, clear=clear, except_errors=True)


def import_system_data():
    """
    Import all local data files to models.
    """
    from django.conf import settings
    from muddery.worldeditor.services import importer

    # load system default data
    default_template = os.path.join(configs.GAME_TEMPLATES, configs.DEFAULT_TEMPLATE)

    # data file's path
    data_path = os.path.join(default_template, settings.WORLD_DATA_FOLDER)
    importer.import_data_path(data_path, clear=False, except_errors=True)

    # localized string file's path
    localized_string_path = os.path.join(data_path, settings.LOCALIZED_STRINGS_FOLDER, settings.LANGUAGE_CODE)
    importer.import_table_path(localized_string_path, settings.LOCALIZED_STRINGS_MODEL, clear=False, except_errors=True)


def init_game_env(gamedir):
    """
    Set the environment to the game dir.
    """
    os.chdir(gamedir)

    # Add gamedir to python path
    sys.path.insert(0, gamedir)

    # Game directory structure
    SETTINGS_DOTPATH = "server.conf.settings"
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_DOTPATH)
    django.setup()


def create_superuser(username, password):
    """
    Create the superuser's account.
    """
    from evennia.accounts.models import AccountDB
    AccountDB.objects.create_superuser(username, '', password)


def create_database():
    """
    Create the game's database.
    """
    # make migrations
    django_args = ["makemigrations"]
    django_kwargs = {}
    try:
        django.core.management.call_command(*django_args, **django_kwargs)
    except django.core.management.base.CommandError as exc:
        raise(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

    django_args = ["makemigrations", "gamedata"]
    django_kwargs = {}
    try:
        django.core.management.call_command(*django_args, **django_kwargs)
    except django.core.management.base.CommandError as exc:
        raise(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

    django_args = ["makemigrations", "worlddata"]
    django_kwargs = {}
    try:
        django.core.management.call_command(*django_args, **django_kwargs)
    except django.core.management.base.CommandError as exc:
        raise(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

    # migrate the database
    django_args = ["migrate"]
    django_kwargs = {}
    try:
        django.core.management.call_command(*django_args, **django_kwargs)
    except django.core.management.base.CommandError as exc:
        raise(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

    django_args = ["migrate", "gamedata"]
    django_kwargs = {"database": "gamedata"}
    try:
        django.core.management.call_command(*django_args, **django_kwargs)
    except django.core.management.base.CommandError as exc:
        raise(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

    django_args = ["migrate", "worlddata"]
    django_kwargs = {"database": "worlddata"}
    try:
        django.core.management.call_command(*django_args, **django_kwargs)
    except django.core.management.base.CommandError as exc:
        raise(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))


def create_editor_database():
    """
    Create the game's database.
    """
    # make migrations
    django_args = ["makemigrations"]
    django_kwargs = {}
    try:
        django.core.management.call_command(*django_args, **django_kwargs)
    except django.core.management.base.CommandError as exc:
        raise(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

    # migrate the database
    django_args = ["migrate"]
    django_kwargs = {}
    try:
        django.core.management.call_command(*django_args, **django_kwargs)
    except django.core.management.base.CommandError as exc:
        raise(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))


def print_info():
    """
    Format info dicts from the Portal/Server for display

    """
    from django.conf import settings

    ind = " " * 8
    info = {
        "servername": settings.GAME_SERVERNAME,
        "version": muddery_version(),
        "status": ""
    }

    def _prepare_dict(dct):
        out = {}
        for key, value in dct.items():
            if isinstance(value, list):
                value = "\n{}".format(ind).join(str(val) for val in value)
            out[key] = value
        return out

    def _strip_empty_lines(string):
        return "\n".join(line for line in string.split("\n") if line.strip())

    # Print server info.
    sdict = _prepare_dict(info)
    info = _strip_empty_lines(configs.SERVER_INFO.format(**sdict))

    maxwidth = max(len(line) for line in info.split("\n"))
    top_border = "-" * (maxwidth - 11) + " Muddery " + "---"
    border = "-" * (maxwidth + 1)
    print("\n" + top_border + "\n" + info + '\n' + border)
