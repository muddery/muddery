# The game's webclient.

import os
from muddery.server.settings import SETTINGS
from server.settings import ServerSettings


def main():
    SETTINGS.update(ServerSettings())
    SETTINGS.LOG_NAME = "muddery_gameserver"
    SETTINGS.LOG_FILE = os.path.join(SETTINGS.LOG_PATH, "gameserver.log")

    from muddery.server.networks.sanic_game_server import SanicGameServer
    SanicGameServer.run()


if __name__ == '__main__':
    # start from the command line
    main()
