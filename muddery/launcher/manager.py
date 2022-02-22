
import time
import os
import traceback
import asyncio
import subprocess
from urllib import request, error
from argparse import ArgumentParser
from muddery.launcher import configs, utils


def print_about():
    """
    Print about info.

    :return:
    """
    print(configs.ABOUT_INFO)


def show_version():
    """
    Show game version.
    """
    print("Muddery version: " + utils.muddery_version())


def init_game(game_name, template=None, port=None):
    """
    Create a new game project.

    :param game_name: game project's name
    :param template: game template's name
    :param port: game server's port.
    :return:
    """
    gamedir = os.path.abspath(os.path.join(configs.CURRENT_DIR, game_name))
    if not port:
        port = 8000

    utils.create_game_directory(gamedir, template, port)
    utils.init_game_env(gamedir)

    print(configs.CREATED_NEW_GAMEDIR.format(
        gamedir=game_name,
        settings_path=os.path.join(game_name, configs.SETTINGS_PATH),
        game_server_port=port,
        world_editor_port=port+2
    ))


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

    # check tables
    try:
        from muddery.server.database.worlddata_db import WorldDataDB
        WorldDataDB.inst().connect()
        has_tables = WorldDataDB.inst().check_tables()
    except Exception as e:
        traceback.print_exc()
        raise

    if not has_tables:
        print(configs.NO_GAME_TABLES)
        return

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

    # Set game environment
    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    # Load settings.
    from muddery.server.settings import SETTINGS as SERVER_SETTINGS
    from server.settings import ServerSettings
    SERVER_SETTINGS.update(ServerSettings())

    # check tables
    try:
        from muddery.server.database.worlddata_db import WorldDataDB
        WorldDataDB.inst().connect()
        has_tables = WorldDataDB.inst().check_tables()
    except Exception as e:
        traceback.print_exc()
        raise

    if not has_tables:
        print(configs.NO_GAME_TABLES)
        return

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


async def get_server_state(gameserver:bool=False, webclient:bool=False, editor:bool=False, req_timeout:float=0) -> dict:
    """
    Check server's state.

    :param:
        gameserver: check the game server
        webclient: check the webclient
        editor: check the world editor
        req_timeout: timeout for waiting state request
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

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    servers = {}

    if gameserver or webclient:
        from muddery.server.settings import SETTINGS as SERVER_SETTINGS
        from server.settings import ServerSettings
        SERVER_SETTINGS.update(ServerSettings())

        if gameserver:
            servers["server"] = {
                "name": "Game server",
                "port": SERVER_SETTINGS.GAME_SERVER_PORT,
                "url": "http://localhost:%s/status" % SERVER_SETTINGS.GAME_SERVER_PORT,
            }

        if webclient:
            servers["webclient"] = {
                "name": "Webclient",
                "port": SERVER_SETTINGS.WEBCLIENT_PORT,
                "url": "http://localhost:%s/status" % SERVER_SETTINGS.WEBCLIENT_PORT,
            }

    if editor:
        from muddery.worldeditor.settings import SETTINGS as WORLDEDITOR_SETTINGS
        from worldeditor.settings import ServerSettings
        WORLDEDITOR_SETTINGS.update(ServerSettings())

        servers["editor"] = {
            "name": "World editor",
            "port": WORLDEDITOR_SETTINGS.WORLD_EDITOR_PORT,
            "url": "http://localhost:%s/status" % WORLDEDITOR_SETTINGS.WORLD_EDITOR_PORT,
        }

    awaits = [asyncio.create_task(async_reqeust(item["url"], timeout=req_timeout)) for item in servers.values()]
    responses = await asyncio.gather(*awaits)

    for key, response in zip(servers, responses):
        servers[key]["running"] = (response == 200)

    return servers


async def wait_server_state(gameserver: bool = False, webclient: bool = False, editor: bool = False, req_timeout: float = 0,
                            total_wait_time: float = 0) -> dict:
    """
    Check server's state until all servers are running.
    
    :param
        gameserver: check the game server
        webclient: check the webclient
        editor: check the world editor
        req_timeout: timeout for waiting state request
        total_wait_time: total time for waiting server states
    :return:
    """
    if req_timeout < 1:
        req_timeout = 1

    if total_wait_time < req_timeout:
        total_wait_time = req_timeout

    wait_time = 0
    states = {}
    while wait_time < total_wait_time:
        time_begin = time.time()
        states = await get_server_state(gameserver, webclient, editor, req_timeout)
        time_end = time.time()

        time_spend = time_end - time_begin
        if time_spend < req_timeout:
            # wait until the request time finished.
            await asyncio.sleep(req_timeout - time_spend)
        wait_time += req_timeout

        all_running = True
        for item in states.values():
            if not item["running"]:
                all_running = False
                break

        if all_running:
            break

    return states


async def show_server_state(gameserver: bool = False, webclient: bool = False, editor: bool = False, req_timeout: float = 0,
                            total_wait_time: float = 0):
    """
    Show server's state.

    :param
        gameserver: check the game server
        webclient: check the webclient
        editor: check the world editor
        req_timeout: timeout for waiting state request
        total_wait_time: total time for waiting server states
    :return:
    """
    states = await wait_server_state(gameserver, webclient, editor, req_timeout, total_wait_time)
    for item in states.values():
        if item["running"]:
            print("%s is running at port %s." % (item["name"], item["port"]))
        else:
            print("%s is not running at port %s." % (item["name"], item["port"]))
    print("")


async def run_servers(server: bool = False, webclient: bool = False, editor: bool = False, restart: bool = False):
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

    if not utils.check_version():
        print(configs.NEED_UPGRADE)
        return

    # Load settings.
    try:
        from muddery.server.settings import SETTINGS
        from server.settings import ServerSettings
        SETTINGS.update(ServerSettings())
    except Exception as e:
        traceback.print_exc()
        raise

    # check tables
    try:
        from muddery.server.database.gamedata_db import GameDataDB
        GameDataDB.inst().connect()
        has_tables = GameDataDB.inst().check_tables()
    except Exception as e:
        traceback.print_exc()
        raise

    if not has_tables:
        print(configs.NO_GAME_TABLES)
        return

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

    await show_server_state(server, webclient, editor, 5, 20)


def kill_servers(server: bool = True, webclient: bool = True, editor: bool = True):
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


def run_server_command(run_func, stop_func, default_port):
    parser = ArgumentParser()
    parser.add_argument(
        "operation",
        nargs='?',
        default="run",
        help=configs.ARG_OPTIONS)
    parser.add_argument(
        '-p', '--port',
        nargs=1,
        action='store',
        dest='port',
        metavar="<N>",
        help="Set game's network ports, recommend to use ports above 10000.")

    args, unknown_args = parser.parse_known_args()
    operation = args.operation

    port = default_port
    if args.port:
        try:
            port = int(args.port[0])
        except:
            print("Port must be a number.")
            return

    if operation == "run":
        # start the server
        run_func(port)
    elif operation == "restart":
        # stop and start a new server
        stop_func()
        run_func(port)
    elif operation == "stop":
        # stop the server
        stop_func()
