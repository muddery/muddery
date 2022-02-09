# The game's webclient.

import sys
from muddery.server.networks.sanic_webclient import run, stop
from muddery.server.settings import SETTINGS
from server.settings import ServerSettings


def main(argv):
    SETTINGS.update(ServerSettings())
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
