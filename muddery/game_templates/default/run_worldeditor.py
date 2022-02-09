# The world editor.

import sys
from muddery.worldeditor.networks.sanic_server import run, stop
from muddery.worldeditor.settings import SETTINGS
from worldeditor.settings import ServerSettings


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
