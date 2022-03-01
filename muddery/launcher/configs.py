#!/usr/bin/env python
"""

"""

import os


MUDDERY_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MUDDERY_LIB = os.path.join(MUDDERY_ROOT, "muddery")
GAME_TEMPLATES = os.path.join(MUDDERY_LIB, "game_templates")

# Game directory structure
SETTING_FILE = "settings.py"
SERVER_DIR = "server"
CONF_DIR = os.path.join(SERVER_DIR, "conf")
SETTINGS_PATH = os.path.join(CONF_DIR, SETTING_FILE)
SETTINGS_DOTPATH = "server.conf.settings"
CURRENT_DIR = os.getcwd()
GAME_DIR = CURRENT_DIR

DEFAULT_TEMPLATE = "default"

CONFIG_FILE = "game.cfg"
VERSION_SECTION = "VERSION"
VERSION_ITEM = "version"
TEMPLATE_ITEM = "template"


# ------------------------------------------------------------
#
# Messages
#
# ------------------------------------------------------------

CREATED_NEW_GAMEDIR = \
    """
    Welcome to Muddery!
    Created a new Muddery game directory '{gamedir}'.

    You can now optionally edit your new settings file
    at {settings_path}. If you don't, the defaults
    will work out of the box. When ready to continue, 'cd' to your
    game directory and run:

        muddery setup

    Then run:
    
        muddery start

    This starts the server for the first time. Make sure to create
    a superuser when asked for it. You should now be able to (by
    default) connect to your server by pointing your web browser to
    
        http://localhost:{game_server_port}
    
    and connect to the game world editor at
    
        http://localhost:{world_editor_port}

    """

ERROR_NO_GAMEDIR = \
    """
    You must run this command inside a valid game directory.
    """

NO_GAME_TABLES = \
    """
    You must run this command inside a valid game directory first

        muddery setup
    """

VERSION_INFO = \
    """
    Muddery {version}
    OS: {os}
    Python: {python}

    {about}
    """

ABOUT_INFO = \
    """
    Muddery online game development system

    Licence: BSD 3-Clause Licence
    Web: http://www.muddery.org
    Maintainer (2015-):   Lu Yijun

    Use -h for command line options.
    """

ERROR_INPUT = \
    """
    Command
    {args} {kwargs}
    raised an error: '{traceback}'.
    """

NEED_UPGRADE = \
    """
    Your game's version is too old. Please run:

        muddery upgrade

    to upgrade your game.
    """

SERVER_INFO = \
    """{servername} Server {version}
    {status}
    """

ARG_OPTIONS = \
        """Actions on installed server. One of:
start   - launch servers
restart - restart servers
stop    - shutdown servers
"""

CMDLINE_HELP = \
"""
Starts or operates the Muddery game server.

usage: muddery operation 
 
operations:
  muddery init <dir> [template] [-p <number>]
    Creates a new game dir at current location.
    arguments:
      <dir>                 The game directory's name.
      [template]            (optional) The game template's name. 
      -p, --port <number>   (optional) Set game's network default ports when init the game, default is 8000.

  muddery setup
    Setup a new created game dir.

  muddery start [-s] [-c] [-e]
    Run game servers.
    arguments:
      -s, --server          Run the game server only.
      -c, --client          Run the web client only.
      -e, --editor          Run the world editor only.

  muddery stop [-s] [-c] [-e]
    Stop game servers.
    arguments:
      -s, --server          Stop the game server only.
      -c, --client          Stop the web client only.
      -e, --editor          Stop the world editor only.

  muddery state             Check servers running states.
  muddery createadmin       Create an administrator account in the world editor.
  muddery upgrade           Upgrade a game directory to the latest version.
  muddery migrate           Migrate databases to new version.
  muddery loaddata          Load game data from the worlddata folder.
  muddery sysdata           Reload system default data.
  muddery -h                -h, --help      Show help messages.
  muddery -v                -v, --version   Show version info.
"""