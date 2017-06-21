#!/usr/bin/env python
"""

"""

from __future__ import print_function

import os


MUDDERY_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

MUDDERY_LIB = os.path.join(MUDDERY_ROOT, "muddery")
MUDDERY_TEMPLATE = os.path.join(MUDDERY_ROOT, "templates")
EVENNIA_LIB = os.path.join(MUDDERY_ROOT, "evennia")

# Game directory structure
SETTING_FILE = "settings.py"
SERVER_DIR = "server"
CONF_DIR = os.path.join(SERVER_DIR, "conf")
SETTINGS_PATH = os.path.join(CONF_DIR, SETTING_FILE)
SETTINGS_DOTPATH = "server.conf.settings"
CURRENT_DIR = os.getcwd()
GAME_DIR = CURRENT_DIR

TEMPLATE_DIR = "game_template"

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

       muddery start

    This starts the server for the first time. Make sure to create
    a superuser when asked for it. You should now be able to (by
    default) connect to your server on server 'localhost', port 4000
    using a telnet/mud client or http://localhost:8000 using your web
    browser. If things don't work, check so those ports are open.

    """

CMDLINE_HELP = \
    """
    Starts or operates the Muddery game server. Also allows for
    initializing a new game directory and manages the game's database.
    You can also pass most standard django-admin arguments and
    options.
    """

VERSION_INFO = \
    """
    Muddery {version}
    OS: {os}
    Python: {python}
    Twisted: {twisted}
    Django: {django}
    Evennia {evennia}{about}
    """

ABOUT_INFO = \
    """
    Muddery text game development system

    Licence: BSD 3-Clause Licence
    Web: http://www.muddery.org
    Forum: http://www.muddery.org/forum
    Maintainer (2015-):   Lu Yijun

    Use -h for command line options.
    """

ERROR_INPUT = \
    """
    Command
    {args} {kwargs}
    raised an error: '{traceback}'.
    """

ERROR_NO_GAMEDIR = \
    """
    You must run this command inside a valid game directory first
    created with

        muddery --init mygamename
    """

NEED_UPGRADE = \
    """
    Your game's version {version} is too old. Please run:

        muddery --upgrade

    to upgrade your game.
    """