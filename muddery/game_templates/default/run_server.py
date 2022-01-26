# The game server.

import sys
from muddery.server.networks.sanic_server import run, stop
from muddery.server.settings import SETTINGS
from server.settings import ServerSettings


def main(argv):
    SETTINGS.update(ServerSettings())
    if len(argv) > 1 and argv[1] == "stop":
        stop()
    else:
        run()


if __name__ == '__main__':
    # start from the command line
    main(sys.argv)
