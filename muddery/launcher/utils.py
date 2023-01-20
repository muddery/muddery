#!/usr/bin/env python
"""

"""

import os
import sys
import shutil
import configparser
import random
import string
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

    from subprocess import check_output, CalledProcessError, STDOUT

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


def create_server_settings_file(gamedir, setting_dict):
    """
    Uses the template settings file to build a working
    settings file.

    Args:
        gamedir: (string) game root's path
        setting_dict: (dict)preset settings.
    """
    settings_path = os.path.join(gamedir, "server", "settings.py")
    with open(settings_path, 'r', encoding="utf-8") as f:
        settings_string = f.read()

    # modify the settings
    settings_string = settings_string.format(**setting_dict)

    with open(settings_path, 'w', encoding="utf-8") as f:
        f.write(settings_string)


def create_editor_settings_file(gamedir, setting_dict):
    """
    Uses the template settings file to build a working
    settings file.

    Args:
        gamedir: (string) game root's path
        setting_dict: (dict)preset settings.
    """
    settings_path = os.path.join(gamedir, "worldeditor", "settings.py")
    with open(settings_path, 'r', encoding="utf-8") as f:
        settings_string = f.read()

    # modify the settings
    settings_string = settings_string.format(**setting_dict)

    with open(settings_path, 'w', encoding="utf-8") as f:
        f.write(settings_string)


def create_webclient_settings(gamedir, setting_dict):
    """
    Uses the template settings file to build a working
    webclient settings file.

    Args:
        gamedir: (string) game root's path
        setting_dict: (dict)preset settings.
    """
    settings_path = os.path.join(gamedir, "webclient", "settings.js")
    with open(settings_path, 'r') as f:
        settings_string = f.read()

    # modify the settings
    settings_string = settings_string.format(**setting_dict)

    with open(settings_path, 'w') as f:
        f.write(settings_string)


def copy_tree(source, destination):
    """
    copy file tree
    """
    if not os.path.exists(destination):
        # If does not exist, create one.
        os.makedirs(destination)
        
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
                

def create_game_directory(gamedir, template, port):
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

    # Create the settings file in the new game dir.
    setting_dict = {
        "WEBCLIENT_PORT": port,
        "GAME_SERVER_PORT": port + 1,
    }
    create_server_settings_file(gamedir, setting_dict)
    create_webclient_settings(gamedir, setting_dict)

    # Create game server's RSA keys.
    from muddery.common.utils.crypto import RSA

    rsa = RSA()
    rsa.generate_key()

    server_private_key_path = os.path.join(gamedir, "server", "keys", "rsa_private.pem")
    with open(server_private_key_path, "wb") as fp:
        fp.write(rsa.export_private_key())

    server_public_key_path = os.path.join(gamedir, "webclient", "keys", "rsa_public.pem")
    with open(server_public_key_path, "wb") as fp:
        fp.write(rsa.export_public_key())

    # Create the world editor's setting file.
    setting_dict = {
        "WORLD_EDITOR_PORT": port + 2,
        "WORLD_EDITOR_SECRET": ''.join(random.sample(string.ascii_letters + string.digits, 32)),
    }
    create_editor_settings_file(gamedir, setting_dict)

    # Create world editor's RSA keys.
    rsa.generate_key()

    server_private_key_path = os.path.join(gamedir, "worldeditor", "keys", "rsa_private.pem")
    with open(server_private_key_path, "wb") as fp:
        fp.write(rsa.export_private_key())

    server_public_key_path = os.path.join(gamedir, "worldeditor", "webclient", "keys", "rsa_public.pem")
    with open(server_public_key_path, "wb") as fp:
        fp.write(rsa.export_public_key())


def check_gamedir(path):
    """
    Check if the path is a game dir.
    """
    settings_path = os.path.join(path, "server", "settings.py")
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
    from muddery.server.settings import SETTINGS
    from muddery.server.utils import importer

    # load custom data
    # data file's path
    data_path = os.path.join(SETTINGS.GAME_DIR, SETTINGS.WORLD_DATA_FOLDER)
    importer.import_data_path(data_path, clear=clear, except_errors=True)

    # localized string file's path
    localized_string_path = os.path.join(data_path, SETTINGS.LOCALIZED_STRINGS_FOLDER, SETTINGS.LANGUAGE_CODE)
    importer.import_table_path(localized_string_path, SETTINGS.LOCALIZED_STRINGS_MODEL, clear=clear, except_errors=True)


def import_system_data():
    """
    Import all local data files to models.
    """
    from muddery.server.settings import SETTINGS
    from muddery.server.utils import importer

    # load system default data
    default_template = os.path.join(configs.GAME_TEMPLATES, configs.DEFAULT_TEMPLATE)

    # data file's path
    data_path = os.path.join(default_template, SETTINGS.WORLD_DATA_FOLDER)
    importer.import_data_path(data_path, clear=False, except_errors=True)

    # localized string file's path
    localized_string_path = os.path.join(data_path, SETTINGS.LOCALIZED_STRINGS_FOLDER, SETTINGS.LANGUAGE_CODE)
    importer.import_table_path(localized_string_path, SETTINGS.LOCALIZED_STRINGS_MODEL, clear=False, except_errors=True)


def init_game_env(gamedir):
    """
    Set the environment to the game dir.
    """
    os.chdir(gamedir)

    # Add gamedir to python path
    if len(sys.path) == 0 or sys.path[0] != gamedir:
        sys.path.insert(0, gamedir)


def print_info():
    """
    Format info dicts from the Portal/Server for display

    """
    from muddery.server.settings import SETTINGS

    ind = " " * 8
    info = {
        "servername": SETTINGS.SERVERNAME,
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


def print_states(states):
    """
    Print server states.
    :param states: {
                        <server's name>: {
                            "name": <server's name>,
                            "port": <port number>,
                            "state": <server state>
                        }
                   }
    :return:
    """
    contents = [["Server", "Port", "State"]]
    for value in states.values():
        contents.append([value["name"], str(value["port"]), value["state"]])

    max_length = [max([len(row[col]) for row in contents]) for col in range(len(contents[0]))]

    for row in contents:
        print("  ", end="")

        for length in max_length:
            print("+", end="")
            print("-" * (length + 4), end="")
        print("+")

        print("  ", end="")
        for i, value in enumerate(row):
            print("|", end="")
            print("  %s  " % value, end="")
            print(" " * (max_length[i] - len(value)), end="")
        print("|")

    print("  ", end="")
    for length in max_length:
        print("+", end="")
        print("-" * (length + 4), end="")
    print("+")


def get_argument_port():
    # The port number from arguments.
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        '-p', '--port',
        nargs=1,
        action='store',
        dest='port',
        metavar="<N>",
        help="Set game's network ports, recommend to use ports above 10000.")

    args, unknown_args = parser.parse_known_args()
    if args.port:
        try:
            port = int(args.port[0])
            return port
        except:
            print("Port must be a number.")
