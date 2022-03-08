# The world editor.

import os
from muddery.server.settings import SETTINGS as GAME_SERVER_SETTINGS
from muddery.worldeditor.settings import SETTINGS as WORLDEDITOR_SETTINGS
from server.settings import ServerSettings as GameServerSettings
from worldeditor.settings import ServerSettings as WorldeditorSettings


def main():
    WORLDEDITOR_SETTINGS.update(WorldeditorSettings())
    WORLDEDITOR_SETTINGS.LOG_NAME = "muddery_worldeditor"
    WORLDEDITOR_SETTINGS.LOG_FILE = os.path.join(WORLDEDITOR_SETTINGS.LOG_PATH, "editor.log")

    GAME_SERVER_SETTINGS.update(GameServerSettings())
    GAME_SERVER_SETTINGS.LOG_NAME = "muddery_worldeditor"

    from muddery.launcher.manager import run_server_command
    from muddery.worldeditor.networks.sanic_server import run, stop
    run_server_command(run, stop, WORLDEDITOR_SETTINGS.WORLD_EDITOR_PORT)


if __name__ == '__main__':
    # start from the command line
    main()
