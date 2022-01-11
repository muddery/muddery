
import os
import traceback
from muddery.launcher import configs, utils
from muddery.server.database.db_manager import DBManager


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
    utils.init_game_env(gamedir)

    # create tables first
    DBManager.inst().create_tables()

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


def show_version(about=False):
    """
    Show system version.

    :param about: show about info.
    :return:
    """
    print(utils.show_version_info(about))


def setup_server():
    """
    Setup the server.
    """
    from muddery.server.server import Server
    Server.inst().create_the_world()
    Server.inst().create_command_handler()


def setup_editor():
    """
    Setup the server.
    """
    if not utils.check_database():
        print("Migrating databases.")
        utils.create_editor_database()

    from muddery.worldeditor.server import Server
    Server.inst()


def collect_static():
    """
    Collect static web files.
    :return:
    """
    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    from muddery.server.conf import settings
    for item in settings.STATICFILES_DIRS:
        source = item[1]
        target = os.path.join(settings.WEBCLIENT_ROOT, item[0])
        utils.copy_tree(source, target)
