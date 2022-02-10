
import os
import traceback
import asyncio
import subprocess
from urllib import request, error
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


def create_server_tables():
    """
    Create database tables.
    :return:
    """
    print("Creating the game server's tables.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    # Load settings.
    try:
        from muddery.server.settings import SETTINGS
        from server.settings import ServerSettings
        SETTINGS.update(ServerSettings())
    except Exception as e:
        traceback.print_exc()
        raise

    # Create tables
    try:
        from muddery.server.database.gamedata_db import GameDataDB
        GameDataDB.inst().connect()
        GameDataDB.inst().create_tables()

        from muddery.server.database.worlddata_db import WorldDataDB
        WorldDataDB.inst().connect()
        WorldDataDB.inst().create_tables()
    except Exception as e:
        traceback.print_exc()
        raise


def create_worldeditor_tables():
    """
    Create database tables.
    :return:
    """
    print("Creating the worldeditor's tables.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    # Load settings.
    try:
        from muddery.worldeditor.settings import SETTINGS
        from worldeditor.settings import ServerSettings
        SETTINGS.update(ServerSettings())
    except Exception as e:
        traceback.print_exc()
        raise

    # Create tables
    try:
        from muddery.worldeditor.database.worldeditor_db import WorldEditorDB
        WorldEditorDB.inst().connect()
        WorldEditorDB.inst().create_tables()
    except Exception as e:
        traceback.print_exc()
        raise


def load_game_data():
    """
    Reload the game's default data.

    :return:
    """
    print("Importing local data.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    # Load settings.
    try:
        from muddery.server.settings import SETTINGS
        from server.settings import ServerSettings
        SETTINGS.update(ServerSettings())
    except Exception as e:
        traceback.print_exc()
        raise

    # connect the db
    try:
        from muddery.server.database.worlddata_db import WorldDataDB
        WorldDataDB.inst().connect()
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


def migrate_database(database_name):
    """
    Migrate databases to the latest Muddery version.

    :return:
    """
    print("Migrating %s." % database_name)

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    try:
        subprocess.Popen("alembic -n %s revision --autogenerate" % database_name).wait()
        subprocess.Popen("alembic -n %s upgrade head" % database_name).wait()
    except Exception as e:
        traceback.print_exc()
        print("Migrate %s error: %s" % (database_name, e))


def collect_webclient_static():
    """
    Collect webclient's static web files.
    :return:
    """
    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    # game webpage files
    try:
        from muddery.server.settings import SETTINGS
        from server.settings import ServerSettings
        SETTINGS.update(ServerSettings())
    except Exception as e:
        traceback.print_exc()
        raise

    for item in SETTINGS.WEBCLIENT_SOURCE_DIRS:
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
    try:
        from muddery.worldeditor.settings import SETTINGS
        from worldeditor.settings import ServerSettings
        SETTINGS.update(ServerSettings())
    except Exception as e:
        traceback.print_exc()
        raise

    for item in SETTINGS.WEBCLIENT_SOURCE_DIRS:
        source = item[1]
        target = item[0]
        utils.copy_tree(source, target)

    print("Worldeditor's static files collected.")


async def wait_server_status(server_process, webclient_process, worldeditor_process, timeout):
    """
    Check server's status.

    :param server_process:
    :param webclient_process:
    :param worldeditor_process:
    :param timeout:
    :return:
    """
    async def async_reqeust(url, timeout):
        try:
            req = request.urlopen(url, timeout=timeout)
            code = req.getcode()
        except error.HTTPError as e:
            code = e.code
        except error.URLError as e:
            code = -1
        return code

    async def get_server_status(server_process, webclient_process, worldeditor_process):
        # get status url
        server_status_url = None
        webclient_status_url = None
        worldeditor_status_url = None

        if server_process or webclient_process:
            try:
                from muddery.server.settings import SETTINGS as SERVER_SETTINGS
                from server.settings import ServerSettings
                SERVER_SETTINGS.update(ServerSettings())
                server_status_url = "http://localhost:%s/status" % SERVER_SETTINGS.WEBSERVER_PORT
                webclient_status_url = "http://localhost:%s/status" % SERVER_SETTINGS.WEBCLIENT_PORT
            except Exception as e:
                traceback.print_exc()
                if server_process:
                    server_process = None
                    print("Can not start the game server.")
                if webclient_process:
                    webclient_process = None
                    print("Can not start the webclient server.")

        if worldeditor_process:
            try:
                from muddery.worldeditor.settings import SETTINGS as WORLDEDITOR_SETTINGS
                from worldeditor.settings import ServerSettings
                WORLDEDITOR_SETTINGS.update(ServerSettings())
                worldeditor_status_url = "http://localhost:%s/status" % WORLDEDITOR_SETTINGS.WORLD_EDITOR_PORT
            except Exception as e:
                traceback.print_exc()
                worldeditor_process = None
                print("Can not start the worldeditor server.")

        while server_process or webclient_process or worldeditor_process:
            awaits = []
            if server_process:
                if server_process.poll() is not None:
                    # process stopped
                    server_process = None
                    print("Can not start the game server.")
                else:
                    awaits.append(asyncio.create_task(async_reqeust(server_status_url, timeout=5)))

            if webclient_process:
                if webclient_process.poll() is not None:
                    # process stopped
                    webclient_process = None
                    print("Can not start the webclient server.")
                else:
                    awaits.append(asyncio.create_task(async_reqeust(webclient_status_url, timeout=5)))

            if worldeditor_process:
                if worldeditor_process.poll() is not None:
                    # process stopped
                    worldeditor_process = None
                    print("Can not start the worldeditor server.")
                else:
                    awaits.append(asyncio.create_task(async_reqeust(worldeditor_status_url, timeout=5)))

            results = await asyncio.gather(*awaits)

            if server_process:
                if results[0] == 200:
                    server_process = None
                    print("Game server is running.")
                results = results[1:]

            if webclient_process:
                if results[0] == 200:
                    webclient_process = None
                    print("Webclient is running.")
                results = results[1:]

            if worldeditor_process:
                if results[0] == 200:
                    worldeditor_process = None
                    print("Worldeditor is running.")

            await asyncio.sleep(1)

    try:
        await asyncio.wait_for(get_server_status(server_process, webclient_process, worldeditor_process), timeout)
        print("All servers are running.")
    except asyncio.TimeoutError:
        print("Can not start all servers.")


def run(server: bool = False, webclient: bool = False, editor: bool = False, restart: bool = False):
    """
    Run servers.

    Args:
        server: run the game server.
        webclient: run the web client.
        editor: run the world editor.
        restart: restart the server
    """
    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    print("Starting ...")

    template = "python %s"

    if restart:
        template += " restart"

    if os.name != "nt":
        template += " &"

    options = {
        "shell": True,
    }

    server_process = None
    if server:
        # Run game servers.
        command = template % "run_server.py"
        server_process = subprocess.Popen(command, **options)

    webclient_process = None
    if webclient:
        # Run web client.
        command = template % "run_webclient.py"
        webclient_process = subprocess.Popen(command, **options)

    worldeditor_process = None
    if editor:
        # Run world editor.
        command = template % "run_worldeditor.py"
        worldeditor_process = subprocess.Popen(command, **options)

    asyncio.run(wait_server_status(server_process, webclient_process, worldeditor_process, 30))


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
