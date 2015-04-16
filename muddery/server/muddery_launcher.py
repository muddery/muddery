#!/usr/bin/env python
"""
MUDDERY SERVER LAUNCHER SCRIPT

This is the start point for running Muddery.

Sets the appropriate environmental variables and launches the server
and portal through the evennia_runner. Run without arguments to get a
menu. Run the script with the -h flag to see usage information.

"""

import os
import sys
import shutil
from argparse import ArgumentParser
from subprocess import check_output, CalledProcessError, STDOUT


MUDDERY_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import muddery
MUDDERY_LIB = os.path.join(os.path.dirname(os.path.abspath(muddery.__file__)))
MUDDERY_TEMPLATE = os.path.join(MUDDERY_ROOT, "templates")
EVENNIA_LIB = os.path.join(MUDDERY_ROOT, "evennia")

# add evennia's path
sys.path.insert(2, EVENNIA_LIB)

import evennia
from evennia.server import evennia_launcher

# Game directory structure
SETTINGFILE = "settings.py"
SERVERDIR = "server"
CONFDIR = os.path.join(SERVERDIR, "conf")
SETTINGS_PATH = os.path.join(CONFDIR, SETTINGFILE)
SETTINGS_DOTPATH = "server.conf.settings"
CURRENT_DIR = os.getcwd()
GAMEDIR = CURRENT_DIR


#------------------------------------------------------------
#
# Messages
#
#------------------------------------------------------------

CREATED_NEW_GAMEDIR = \
    """
    Welcome to Muddery!
    Created a new Muddery game directory '{gamedir}'.

    You can now optionally edit your new settings file
    at {settings_path}. If you don't, the defaults
    will work out of the box. When ready to continue, 'cd' to your
    game directory and run:

       muddery migrate

    This initializes the database. To start the server for the first
    time, run:

       muddery -i start

    Make sure to create a superuser when asked for it. You should now
    be able to (by default) connect to your server on server
    'localhost', port 4000 using a telnet/mud client or
    http://localhost:8000 using your web browser. If things don't
    work, check so those ports are open.

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


ABOUT_INFO= \
    """
    Muddery text game development system

    Licence: BSD 3-Clause Licence
    Web: http://www.muddery.org
    Forum: http://www.muddery.org/forum
    Maintainer (2015-):   Lu Yijun

    Use -h for command line options.
    """


MENU = \
    """
    +----Muddery Launcher-------------------------------------------+
    |                                                               |
    +--- Starting --------------------------------------------------+
    |                                                               |
    |  1) (normal):       All output to logfiles                    |
    |  2) (server devel): Server logs to terminal (-i option)       |
    |  3) (portal devel): Portal logs to terminal                   |
    |  4) (full devel):   Both Server and Portal logs to terminal   |
    |                                                               |
    +--- Restarting ------------------------------------------------+
    |                                                               |
    |  5) Reload the Server                                         |
    |  6) Reload the Portal (only works with portal/full debug)     |
    |                                                               |
    +--- Stopping --------------------------------------------------+
    |                                                               |
    |  7) Stopping both Portal and Server                           |
    |  8) Stopping only Server                                      |
    |  9) Stopping only Portal                                      |
    |                                                               |
    +---------------------------------------------------------------+
    |  h) Help              i) About info               q) Abort    |
    +---------------------------------------------------------------+
    """


#------------------------------------------------------------
#
# Functions
#
#------------------------------------------------------------

def muddery_version():
    """
    Get the Muddery version info from the main package.
    """
    version = "Unknown"
    try:
        import muddery
        version = muddery.__version__
    except ImportError:
        pass
    try:
        version = "%s (rev %s)" % (version, check_output("git rev-parse --short HEAD", shell=True, cwd=MUDDERY_ROOT, stderr=STDOUT).strip())
    except (IOError, CalledProcessError):
        pass
    return version

MUDDERY_VERSION = muddery_version()


def create_secret_key():
    """
    Randomly create the secret key for the settings file
    """
    import random
    import string
    secret_key = list((string.letters +
        string.digits + string.punctuation).replace("\\", "").replace("'", '"'))
    random.shuffle(secret_key)
    secret_key = "".join(secret_key[:40])
    return secret_key


def create_settings_file():
    """
    Uses the template settings file to build a working
    settings file.
    """
    settings_path = os.path.join(GAMEDIR, "server", "conf", "settings.py")
    with open(settings_path, 'r') as f:
        settings_string = f.read()

    # tweak the settings
    setting_dict = {"evennia_settings_default": os.path.join(evennia_launcher.EVENNIA_LIB, "settings_default.py"),
                    "muddery_settings_default": os.path.join(MUDDERY_LIB, "settings_default.py"),
                    "servername":"\"%s\"" % GAMEDIR.rsplit(os.path.sep, 1)[1].capitalize(),
                    "secret_key":"\'%s\'" % create_secret_key()}

    # modify the settings
    settings_string = settings_string.format(**setting_dict)

    with open(settings_path, 'w') as f:
        f.write(settings_string)


def create_game_directory(dirname, template):
    """
    Initialize a new game directory named dirname
    at the current path. This means copying the
    template directory from muddery's root.
    """
    global GAMEDIR
    GAMEDIR = os.path.abspath(os.path.join(CURRENT_DIR, dirname))
    if os.path.exists(GAMEDIR):
        print "Cannot create new Muddery game dir: '%s' already exists." % dirname
        sys.exit()
    
    template_dir = os.path.join(MUDDERY_TEMPLATE, template)
    if not os.path.exists(template_dir):
        print "Template '%s' does not exist. You should choose an example in template/ or leave it blank." % template
        sys.exit()
    # copy template directory
    shutil.copytree(template_dir, GAMEDIR)
    # pre-build settings file in the new GAMEDIR
    create_settings_file()


def show_version_info(about=False):
    """
    Display version info
    """
    import os, sys
    import twisted
    import django

    return VERSION_INFO.format(version=MUDDERY_VERSION,
                             about=ABOUT_INFO if about else "",
                             os=os.name, python=sys.version.split()[0],
                             twisted=twisted.version.short(),
                             django=django.get_version(),
                             evennia=evennia_launcher.evennia_version(),)


def run_menu():
    """
    This launches an interactive menu.
    """
    while True:
        # menu loop

        print MENU
        inp = raw_input(" option > ")

        # quitting and help
        if inp.lower() == 'q':
            return
        elif inp.lower() == 'h':
            print HELP_ENTRY
            raw_input("press <return> to continue ...")
            continue
        elif inp.lower() in ('v', 'i', 'a'):
            print show_version_info(about=True)
            raw_input("press <return> to continue ...")
            continue

        # options
        try:
            inp = int(inp)
        except ValueError:
            print "Not a valid option."
            continue
        if inp == 1:
            # start everything, log to log files
            server_operation("start", "all", False, False)
        elif inp == 2:
            # start everything, server interactive start
            server_operation("start", "all", True, False)
        elif inp == 3:
            # start everything, portal interactive start
            server_operation("start", "server", False, False)
            server_operation("start", "portal", True, False)
        elif inp == 4:
            # start both server and portal interactively
            server_operation("start", "server", True, False)
            server_operation("start", "portal", True, False)
        elif inp == 5:
            # reload the server
            server_operation("reload", "server", None, None)
        elif inp == 6:
            # reload the portal
            server_operation("reload", "portal", None, None)
        elif inp == 7:
            # stop server and portal
            server_operation("stop", "all", None, None)
        elif inp == 8:
            # stop server
            server_operation("stop", "server", None, None)
        elif inp == 9:
            # stop portal
            server_operation("stop", "portal", None, None)
        else:
            print "Not a valid option."
            continue
        return


def main():
    """
    Run the muddery main program.
    """

    # set up argument parser

    parser = ArgumentParser(description=CMDLINE_HELP)
    parser.add_argument('-v', '--version', action='store_true',
                      dest='show_version', default=False,
                      help="Show version info.")
    parser.add_argument('-i', '--interactive', action='store_true',
                      dest='interactive', default=False,
                      help="Start given processes in interactive mode.")
    parser.add_argument('--init', action='store', dest="init", metavar="game_name [template]",
                        help="Creates a new game directory 'game_name' at the current location (from optional template).")
    parser.add_argument('-l', nargs='+', action='store', dest='listsetting', metavar="key",
                      help="List values for server settings. Use 'all' to list all available keys.")
    parser.add_argument('--profiler', action='store_true', dest='profiler', default=False,
                      help="Start given server component under the Python profiler.")
    parser.add_argument('--dummyrunner', nargs=1, action='store', dest='dummyrunner', metavar="N",
                        help="Tests a running server by connecting N dummy players to it.")
    parser.add_argument('--settings', nargs=1, action='store', dest='altsettings', default=None, metavar="filename.py",
                      help="Start evennia with alternative settings file in gamedir/server/conf/.")
    parser.add_argument("option", nargs='?', default="noop",
                        help="Operational mode: 'start', 'stop', 'restart' or 'menu'.")
    parser.add_argument("service", metavar="component", nargs='?', default="all",
                        help="Server component to operate on: 'server', 'portal' or 'all' (default).")
    parser.epilog = "Example django-admin commands: 'migrate', 'flush', 'shell' and 'dbshell'. " \
                    "See the django documentation for more django-admin commands."

    args, unknown_args = parser.parse_known_args()

    # handle arguments
    option, service = args.option, args.service

    # make sure we have everything
    evennia_launcher.check_main_evennia_dependencies()

    if not args:
        # show help pane
        print CMDLINE_HELP
        sys.exit()
    elif args.init:
        # initialization of game directory
        if option == "noop":
            option = "default"
        create_game_directory(args.init, option)
        print CREATED_NEW_GAMEDIR.format(gamedir=args.init,
                                         settings_path=os.path.join(args.init, SETTINGS_PATH))
        sys.exit()

    if args.show_version:
        # show the version info
        print show_version_info(option=="help")
        sys.exit()

    if args.altsettings:
        evennia_launcher.main()

    if option == 'menu':
        # launch menu for operation
        evennia_launcher.init_game_directory(CURRENT_DIR, check_db=True)
        run_menu()
    elif option != "noop":
        # pass-through to evennia
        evennia_launcher.main()
    else:
        # no input; print muddery info
        print ABOUT_INFO


if __name__ == '__main__':
    # start Muddery from the command line
    main()
