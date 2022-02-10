# The world editor.

import sys
from muddery.worldeditor.networks.sanic_server import run, stop
from muddery.server.settings import SETTINGS as GAME_SERVER_SETTINGS
from server.settings import ServerSettings as GameServerSettings
from muddery.worldeditor.settings import SETTINGS as WORLDEDITOR_SETTINGS
from worldeditor.settings import ServerSettings as WorldeditorSettings


def main(argv):
    GAME_SERVER_SETTINGS.update(GameServerSettings())
    WORLDEDITOR_SETTINGS.update(WorldeditorSettings())

    if len(argv) == 1:
        # start the server
        run()
    elif len(argv) == 2:
        if argv[1] == "stop":
            # stop the server
            stop()
        elif argv[1] == "restart":
            # stop and start a new server
            stop()
            run()


if __name__ == '__main__':
    # start from the command line
    main(sys.argv)
