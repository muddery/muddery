# The game's webclient.

from muddery.server.settings import SETTINGS
from server.settings import ServerSettings


def main():
    SETTINGS.update(ServerSettings())

    from muddery.launcher.manager import run_server_command
    from muddery.server.networks.sanic_webclient import run, stop
    run_server_command(run, stop, SETTINGS.WEBCLIENT_PORT)


if __name__ == '__main__':
    # start from the command line
    main()
