
import time
import os
import traceback
import asyncio
import subprocess
import httpx
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


def create_editor_admin():
    """
    Create a new account.
    """
    check_editor_admin(True)


def check_editor_admin(force_create=False):
    """
    Check if there is an admin account in the world editor. If not, create a new account.
    """
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

    # Check accounts.
    try:
        from muddery.worldeditor.database.worldeditor_db import WorldEditorDB
        from muddery.worldeditor.dao.accounts import Accounts

        WorldEditorDB.inst().connect()

        # Check admin accounts.
        if force_create or (Accounts.inst().count() == 0):
            # Create a new account.
            print("\nCreating the world editor account. Enter empty username to skip.")
            username = input("Please input your username: ")
            if not username:
                return

            import getpass
            password = getpass.getpass("Please input your password: ")

            if Accounts.inst().has(username):
                print("Username already exists.")
                return

            try:
                from muddery.common.utils.password import hash_password, make_salt
                salt = make_salt()
                password = hash_password(password, salt)
                Accounts.inst().add(username, password, salt, "ADMIN")
                print("Account created.\n")
            except Exception as e:
                print("Got error: %s" % e)

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


async def call_server_command(command:str, gameserver:bool=False, webclient:bool=False, editor:bool=False, req_timeout:float=0) -> dict:
    """
    Call server's command.

    :param:
        command: command to run
        gameserver: call the game server
        webclient: call the webclient
        editor: call the world editor
        req_timeout: timeout for waiting state request
    :return:
    """
    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    servers = {}

    if gameserver or webclient:
        from muddery.server.settings import SETTINGS as SERVER_SETTINGS
        from server.settings import ServerSettings
        SERVER_SETTINGS.update(ServerSettings())

        if gameserver:
            servers["gameserver"] = {
                "name": SERVER_SETTINGS.GAME_SERVER_NAME,
                "port": SERVER_SETTINGS.GAME_SERVER_PORT,
                "url": "http://localhost:%s/%s" % (SERVER_SETTINGS.GAME_SERVER_PORT, command),
            }

        if webclient:
            servers["webclient"] = {
                "name": SERVER_SETTINGS.WEBCLIENT_SERVER_NAME,
                "port": SERVER_SETTINGS.WEBCLIENT_PORT,
                "url": "http://localhost:%s/%s" % (SERVER_SETTINGS.WEBCLIENT_PORT, command),
            }

    if editor:
        from muddery.worldeditor.settings import SETTINGS as WORLDEDITOR_SETTINGS
        from worldeditor.settings import ServerSettings
        WORLDEDITOR_SETTINGS.update(ServerSettings())

        servers["editor"] = {
            "name": WORLDEDITOR_SETTINGS.WORLD_EDITOR_SERVER_NAME,
            "port": WORLDEDITOR_SETTINGS.WORLD_EDITOR_PORT,
            "url": "http://localhost:%s/%s" % (WORLDEDITOR_SETTINGS.WORLD_EDITOR_PORT, command),
        }

    async def async_reqeust(client, url, timeout):
        try:
            req = await client.get(url, timeout=timeout)
            code = req.status_code
        except httpx.ConnectError as e:
            code = -3
        except httpx.ConnectTimeout as e:
            code = -2
        except Exception as e:
            code = -1
        return code

    async with httpx.AsyncClient() as client:
        awaits = [asyncio.create_task(async_reqeust(client, item["url"], timeout=req_timeout)) for item in servers.values()]
        responses = await asyncio.gather(*awaits)

    for key, response in zip(servers, responses):
        servers[key]["success"] = (response == 200)

    return servers


async def check_server_state(gameserver:bool=False, webclient:bool=False, editor:bool=False, req_timeout:float=0) -> dict:
    """
    Check server's state.
    """
    return await call_server_command("state", gameserver, webclient, editor, req_timeout)


async def wait_server_run(gameserver: bool = False, webclient: bool = False, editor: bool = False,
                          req_timeout: float = 0, total_wait_time: float = 0) -> dict:
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
    responses = {}
    while wait_time < total_wait_time:
        time_begin = time.time()
        responses = await check_server_state(gameserver, webclient, editor, req_timeout)

        all_running = True
        for value in responses.values():
            if not value["success"]:
                all_running = False
                break

        if all_running:
            break

        time_end = time.time()
        time_spend = time_end - time_begin
        if time_spend < req_timeout and wait_time < total_wait_time:
            # wait until the request time finished.
            await asyncio.sleep(req_timeout - time_spend)
        wait_time += req_timeout

    return responses


async def wait_server_stop(gameserver: bool = False, webclient: bool = False, editor: bool = False,
                           req_timeout: float = 0, total_wait_time: float = 0) -> dict:
    """
    Check server's state until all servers stopped.

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
    responses = {}
    while wait_time < total_wait_time:
        time_begin = time.time()
        responses = await check_server_state(gameserver, webclient, editor, req_timeout)

        all_stopped = True
        for value in responses.values():
            value["success"] = not value["success"]
            if not value["success"]:
                all_stopped = False
                break

        if all_stopped:
            break

        time_end = time.time()
        time_spend = time_end - time_begin
        if time_spend < req_timeout and wait_time < total_wait_time:
            # wait until the request time finished.
            await asyncio.sleep(req_timeout - time_spend)
        wait_time += req_timeout

    return responses


async def show_server_state(gameserver: bool = False, webclient: bool = False, editor: bool = False):
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
    states = await check_server_state(gameserver, webclient, editor, 3)
    for value in states.values():
        if value["success"]:
            value["state"] = "Running"
        else:
            value["state"] = "Stopped"

    print()
    utils.print_states(states)
    print()


async def run_servers(gameserver: bool = False, webclient: bool = False, editor: bool = False,
                      check_running_state: bool = True, mute: bool = False):
    """
    Run servers.

    Args:
        gameserver: run the game server.
        webclient: run the web client.
        editor: run the world editor.
        check_running_state: check servers states before start.
        mute: not show messages.
    """
    run_gameserver, run_webclient, run_editor = gameserver, webclient, editor
    if check_running_state:
        # Check servers states.
        running_states = await check_server_state(gameserver, webclient, editor, 3)

        if gameserver and running_states["gameserver"]["success"]:
            run_gameserver = False

        if webclient and running_states["webclient"]["success"]:
            run_webclient = False

        if editor and running_states["editor"]["success"]:
            run_editor = False

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

    if not mute:
        print("Starting ...")

    template = "python %s"

    if os.name != "nt":
        template += " &"

    options = {
        "shell": True,
    }

    server_process = None
    if run_gameserver:
        # Run game servers.
        command = template % "run_server.py"
        server_process = subprocess.Popen(command, **options)

    webclient_process = None
    if run_webclient:
        # Run web client.
        command = template % "run_webclient.py"
        webclient_process = subprocess.Popen(command, **options)

    worldeditor_process = None
    if run_editor:
        # Run world editor.
        command = template % "run_worldeditor.py"
        worldeditor_process = subprocess.Popen(command, **options)

    check_states = await wait_server_run(run_gameserver, run_webclient, run_editor, 3, 15)

    if check_running_state:
        states = running_states
        for value in states.values():
            value["success"] = not value["success"]
            if not value["success"]:
                value["state"] = "Already Running"
    else:
        states = check_states

    for key, value in check_states.items():
        states[key]["success"] = value["success"]
        if value["success"]:
            states[key]["state"] = "Running"
        else:
            states[key]["state"] = "NOT Running"

    if not mute:
        print()
        utils.print_states(states)
        print()

    return states


async def kill_servers(gameserver: bool = False, webclient: bool = False, editor: bool = False, mute: bool = False):
    """
    kill servers.

    Args:
        gameserver: kill the game server.
        webclient: kill the web client.
        editor: kill the world editor.
        mute: not show messages.
    """
    if not mute:
        print("Stopping ...")

    stop_states = await call_server_command("terminate", gameserver, webclient, editor, 10)

    check_gameserver, check_webclient, check_editor = gameserver, webclient, editor
    if gameserver and not stop_states["gameserver"]["success"]:
        check_gameserver = False

    if webclient and not stop_states["webclient"]["success"]:
        check_webclient = False

    if editor and not stop_states["editor"]["success"]:
        check_editor = False

    check_states = await wait_server_stop(check_gameserver, check_webclient, check_editor, 3, 15)

    states = stop_states
    for value in states.values():
        if not value["success"]:
            value["state"] = "NOT Running"

    for key, value in check_states.items():
        states[key]["success"] = value["success"]
        if value["success"]:
            states[key]["state"] = "Stopped"
        else:
            states[key]["state"] = "NOT Stopped"

    if not mute:
        print()
        utils.print_states(states)
        print()

    return states


async def restart_servers(gameserver: bool = True, webclient: bool = True, editor: bool = True):
    """
    Restart servers.

    :param gameserver:
    :param webclient:
    :param editor:
    :return:
    """
    print("Restarting ...")

    stop_states = await kill_servers(gameserver, webclient, editor, mute=True)

    run_gameserver, run_webclient, run_editor = gameserver, webclient, editor
    if gameserver and not stop_states["gameserver"]["success"]:
        run_gameserver = False

    if webclient and not stop_states["webclient"]["success"]:
        run_webclient = False

    if editor and not stop_states["editor"]["success"]:
        run_editor = False

    running_states = await run_servers(run_gameserver, run_webclient, run_editor, check_running_state=False, mute=True)

    states = stop_states
    for value in states.values():
        if not value["success"]:
            value["state"] = "Not Running"

    for key, value in running_states.items():
        states[key]["success"] = value["success"]
        if value["success"]:
            states[key]["state"] = "Restarted"
        else:
            states[key]["state"] = "NOT Restarted"

    print()
    utils.print_states(states)
    print()

    return states
