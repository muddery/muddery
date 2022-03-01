# The game server.

import os
from muddery.server.settings import SETTINGS
from server.settings import ServerSettings


def main():
    SETTINGS.update(ServerSettings())
    SETTINGS.LOG_NAME = "muddery_gameserver"
    SETTINGS.LOG_FILE = os.path.join(SETTINGS.LOG_PATH, "server.log")

    from muddery.launcher.manager import run_server_command
    from muddery.server.networks.sanic_server import run, stop
    run_server_command(run, stop, SETTINGS.GAME_SERVER_PORT)


if __name__ == '__main__':
    # start from the command line
    main()
