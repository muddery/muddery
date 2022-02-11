# The game server.

from muddery.launcher.manager import run_server_command
from muddery.server.networks.sanic_server import run, stop
from muddery.server.settings import SETTINGS
from server.settings import ServerSettings


def main():
    SETTINGS.update(ServerSettings())
    run_server_command(run, stop, SETTINGS.GAME_SERVER_PORT)


if __name__ == '__main__':
    # start from the command line
    main()
