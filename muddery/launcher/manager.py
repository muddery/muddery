
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


def collect_webclient_static():
    """
    Collect webclient's static web files.
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

    print("Webclient's static files collected.")


def collect_worldeditor_static():
    """
    Collect worldeditor's static web files.
    :return:
    """
    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    # world editor webpage files
    from muddery.worldeditor.server import SETTINGS as EDITOR_SETTINGS
    for item in EDITOR_SETTINGS.WEBCLIENT_SOURCE_DIRS:
        source = item[1]
        target = item[0]
        utils.copy_tree(source, target)

    print("Worldeditor's static files collected.")


def run(server: bool = True, webclient: bool = True, editor: bool = True):
    """
    Run servers.

    Args:
        server: run the game server.
        webclient: run the web client.
        editor: run the world editor.
    """
    import subprocess

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    print("Starting ...")

    if os.name == "nt":
        template = "python %s"
    else:
        template = "python %s &"

    options = {
        "shell": True,
    }

    if server:
        # Run game servers.
        command = template % "run_server.py"
        subprocess.Popen(command, **options)

    if webclient:
        # Run web client.
        command = template % "run_webclient.py"
        subprocess.Popen(command, **options)

    if editor:
        # Run world editor.
        command = template % "run_worldeditor.py"
        subprocess.Popen(command, **options)


def kill(server: bool = True, webclient: bool = True, editor: bool = True):
    """
    kill servers.

    Args:
        server: kill the game server.
        webclient: kill the web client.
        editor: kill the world editor.
    """
    import subprocess

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    print("Stopping ...")

    if os.name == "nt":
        template = "python %s"
    else:
        template = "python %s &"

    options = {
        "shell": True,
    }

    server_process = None
    if server:
        # Run game servers.
        command = template % "run_server.py stop"
        server_process = subprocess.Popen(command, **options)

    webclient_process = None
    if webclient:
        # Run web client.
        command = template % "run_webclient.py stop"
        webclient_process = subprocess.Popen(command, **options)

    worldeditor_process = None
    if editor:
        # Run world editor.
        command = template % "run_worldeditor.py stop"
        worldeditor_process = subprocess.Popen(command, **options)

    if server_process:
        server_process.wait()

    if webclient_process:
        webclient_process.wait()

    if worldeditor_process:
        worldeditor_process.wait()
