# The world editor.

import sys
from muddery.worldeditor.networks.sanic_server import run, stop
from muddery.worldeditor.settings import SETTINGS
from worldeditor.settings import ServerSettings


def main(argv):
    SETTINGS.update(ServerSettings())
    if len(argv) > 1 and argv[1] == "stop":
        stop()
    else:
        run()


if __name__ == '__main__':
    # start from the command line
    main(sys.argv)
