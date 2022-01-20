
import os
import traceback
from muddery.launcher import configs, utils


def print_help():
    """
    Print help messages.
    """
    print(configs.CMDLINE_HELP)


def print_about():
    """
    Print about info.

    :return:
    """
    print(configs.ABOUT_INFO)


def init_game(game_name, template=None, port=None):
    """
    Create a new game project.

    :param game_name: game project's name
    :param template: game template's name
    :param port: game server's port.
    :return:
    """
    gamedir = os.path.abspath(os.path.join(configs.CURRENT_DIR, game_name))
    utils.create_game_directory(gamedir, template, port)
    utils.init_game_env(gamedir)

    print(configs.CREATED_NEW_GAMEDIR.format(gamedir=game_name,
                                             settings_path=os.path.join(game_name, configs.SETTINGS_PATH),
                                             port=port if port else 8000))


def upgrade_game(template=None):
    """
    Upgrade the game project to the latest Muddery version.

    :param template: game template's name
    :return:
    """
    if not utils.check_gamedir(configs.CURRENT_DIR):
        raise Exception

    from muddery.launcher.upgrader.upgrade_handler import UPGRADE_HANDLER
    gamedir = os.path.abspath(configs.CURRENT_DIR)
    UPGRADE_HANDLER.upgrade_game(gamedir, template, configs.MUDDERY_LIB)


def load_game_data():
    """
    Reload the game's default data.

    :return:
    """
    print("Importing local data.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)

    # Load settings.
    try:
        from muddery.server.settings import SETTINGS
        from server.settings import ServerSettings
        SETTINGS.update(ServerSettings())
    except Exception as e:
        traceback.print_exc()
        raise

    try:
        utils.init_game_env(gamedir)
    except Exception as e:
        traceback.print_exc()
        raise

    # create tables first
    try:
        from muddery.server.database.db_manager import DBManager
        DBManager.inst().connect()
        DBManager.inst().create_tables()
    except Exception as e:
        traceback.print_exc()
        raise

    # load local data
    try:
        utils.import_local_data(clear=True)
        print("Import local data success.")
    except Exception as e:
        traceback.print_exc()
        raise


def load_system_data():
    """
    Reload Muddery's system data.

    :return:
    """
    print("Importing system data.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    # load system data
    try:
        utils.import_system_data()
        print("Import system data success.")
    except Exception as e:
        traceback.print_exc()
        raise


def migrate_database():
    """
    Migrate databases to the latest Muddery version.

    :return:
    """
    print("Migrating databases.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    try:
        from muddery.server.server import Server
        Server.inst()
    except Exception as e:
        traceback.print_exc()
        print("Migrate database error: %s" % e)


def collect_static():
    """
    Collect static web files.
    :return:
    """
    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    # game webpage files
    from muddery.server.server import SETTINGS as SERVER_SETTINGS
    for item in SERVER_SETTINGS.WEBCLIENT_SOURCE_DIRS:
        source = item[1]
        target = item[0]
        utils.copy_tree(source, target)

    # world editor webpage files
    from muddery.worldeditor.server import SETTINGS as EDITOR_SETTINGS
    for item in EDITOR_SETTINGS.WEBCLIENT_SOURCE_DIRS:
        source = item[1]
        target = item[0]
        utils.copy_tree(source, target)

    print("Collect static files success.")
