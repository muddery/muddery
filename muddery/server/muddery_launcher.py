#!/usr/bin/env python
"""
MUDDERY SERVER LAUNCHER SCRIPT

This is adapt from evennia/evennia/server/evennia_launcher.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

This is the start point for running Muddery.

Sets the appropriate environmental variables and launches the server
and portal through the evennia_runner. Run without arguments to get a
menu. Run the script with the -h flag to see usage information.
"""

from __future__ import print_function

import os
import sys
import shutil
import django.core.management
from argparse import ArgumentParser
from subprocess import check_output, CalledProcessError, STDOUT


MUDDERY_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MUDDERY_LIB = os.path.join(MUDDERY_ROOT, "muddery")
MUDDERY_TEMPLATE = os.path.join(MUDDERY_ROOT, "templates")
EVENNIA_LIB = os.path.join(MUDDERY_ROOT, "evennia")

# add evennia's path
sys.path.insert(1, EVENNIA_LIB)

from evennia.server import evennia_launcher

# Game directory structure
SETTINGFILE = "settings.py"
SERVER_DIR = "server"
CONF_DIR = os.path.join(SERVER_DIR, "conf")
SETTINGS_PATH = os.path.join(CONF_DIR, SETTINGFILE)
SETTINGS_DOTPATH = "server.conf.settings"
CURRENT_DIR = os.getcwd()
GAME_DIR = CURRENT_DIR


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

       muddery start

    This starts the server for the first time. Make sure to create
    a superuser when asked for it. You should now be able to (by
    default) connect to your server on server 'localhost', port 4000
    using a telnet/mud client or http://localhost:8000 using your web
    browser. If things don't work, check so those ports are open.

    """

UPGRADED_GAMEDIR = \
    """
    Your game directory '{gamedir}' has been upgraded to
    muddery version {version}.
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
        rev = check_output("git rev-parse --short HEAD", shell=True, cwd=MUDDERY_ROOT, stderr=STDOUT).strip()
        version = "%s (rev %s)" % (version, rev)
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
                       string.digits +
                       string.punctuation).replace("\\", "").replace("'", '"'))
    random.shuffle(secret_key)
    secret_key = "".join(secret_key[:40])
    return secret_key


def create_settings_file():
    """
    Uses the template settings file to build a working
    settings file.
    """
    settings_path = os.path.join(GAME_DIR, "server", "conf", "settings.py")
    with open(settings_path, 'r') as f:
        settings_string = f.read()

    # tweak the settings
    setting_dict = {"evennia_settings_default": os.path.join(evennia_launcher.EVENNIA_LIB, "settings_default.py"),
                    "muddery_settings_default": os.path.join(MUDDERY_LIB, "settings_default.py"),
                    "servername":"'%s'" % GAME_DIR.rsplit(os.path.sep, 1)[1].capitalize(),
                    "secret_key":"'%s'" % create_secret_key()}

    # modify the settings
    settings_string = settings_string.format(**setting_dict)

    with open(settings_path, 'w') as f:
        f.write(settings_string)


def create_game_directory(gamedir, template):
    """
    Initialize a new game directory named dirname
    at the current path. This means copying the
    template directory from muddery's root.
    """
    
    def copy_tree(source, destination):
        """
        copy file tree
        """
        if not os.path.exists(destination):
            # If does not exist, create one.
            os.mkdir(destination)
        
        # traverse files and folders
        names = os.listdir(source)
        for name in names:
            srcname = os.path.join(source, name)
            dstname = os.path.join(destination, name)
            try:
                if os.path.isdir(srcname):
                    # If it is a folder, copy it recursively.
                    copy_tree(srcname, dstname)
                else:
                    # Copy file.
                    shutil.copy2(srcname, dstname)
            except Exception, e:
                print("Can not copy file:%s to %s for %s." % (srcname, dstname, e))


    global GAME_DIR
    GAME_DIR = gamedir
    if os.path.exists(GAME_DIR):
        print("Cannot create new Muddery game dir: '%s' already exists." % gamedir)
        sys.exit()

    template_dir = ""
    if template:
        template_dir = os.path.join(MUDDERY_TEMPLATE, template)
        if not os.path.exists(template_dir):
            print('Sorry, template "%s" does not exist.\nThese are available templates:' % template)
            dirs = os.listdir(MUDDERY_TEMPLATE)
            for dir in dirs:
                full_path = os.path.join(MUDDERY_TEMPLATE, dir)
                if os.path.isdir(full_path):
                    print("  %s" % dir)
            print("")
            sys.exit()

    # copy default template directory
    default_template = os.path.join(MUDDERY_LIB, "game_template")
    shutil.copytree(default_template, GAME_DIR)

    # copy version file
    version_src = os.path.join(MUDDERY_LIB, "VERSION.txt")
    version_dest = os.path.join(GAME_DIR, "muddery_version.txt")
    shutil.copy2(version_src, version_dest)

    if template_dir:
        copy_tree(template_dir, GAME_DIR)

    # pre-build settings file in the new GAME_DIR
    create_settings_file()


def show_version_info(about=False):
    """
    Display version info
    """
    import os, sys
    import twisted
    import django
    import evennia

    return VERSION_INFO.format(version=MUDDERY_VERSION,
                               about=ABOUT_INFO if about else "",
                               os=os.name, python=sys.version.split()[0],
                               twisted=twisted.version.short(),
                               django=django.get_version(),
                               evennia=evennia.__version__,)


def main():
    """
    Run the muddery main program.
    """

    # set up argument parser

    parser = ArgumentParser(description=CMDLINE_HELP)
    parser.add_argument('-v', '--version', action='store_true',
                        dest='show_version', default=False,
                        help="Show version info.")
    # parser.add_argument('-i', '--interactive', action='store_true',
    #                     dest='interactive', default=False,
    #                     help="Start given processes in interactive mode.")
    parser.add_argument('--init', nargs='+', action='store', dest="init", metavar="game_name [template]",
                        help="Creates a new game directory 'game_name' at the current location (from optional template).")
    parser.add_argument('-l', nargs='+', action='store', dest='listsetting', metavar="key",
                        help="List values for server settings. Use 'all' to list all available keys.")
    parser.add_argument('--profiler', action='store_true', dest='profiler', default=False,
                        help="Start given server component under the Python profiler.")
    parser.add_argument('--dummyrunner', nargs=1, action='store', dest='dummyrunner', metavar="N",
                        help="Tests a running server by connecting N dummy players to it.")
    parser.add_argument('--settings', nargs=1, action='store', dest='altsettings', default=None, metavar="filename.py",
                        help="Start evennia with alternative settings file in gamedir/server/conf/.")
    parser.add_argument('--upgrade', nargs='+', action='store', dest="upgrade", metavar="game_name [template]",
                        help="Upgrade a game directory 'game_name' to the latest version.")
    parser.add_argument("option", nargs='?', default="noop",
                        help="Operational mode: 'start', 'stop' or 'restart'.")
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
        print(CMDLINE_HELP)
        sys.exit()
    elif args.init:
        # initialization of game directory
        game_name = args.init[0]
        template = None
        if len(args.init) > 1:
            template = args.init[1]

        gamedir = os.path.abspath(os.path.join(CURRENT_DIR, game_name))
        create_game_directory(gamedir, template)

        os.chdir(gamedir)
        evennia_launcher.init_game_directory(GAME_DIR, check_db=False)

        try:
            django_args = ["makemigrations"]
            django_kwargs = {}
            django.core.management.call_command(*django_args, **django_kwargs)
        except django.core.management.base.CommandError, exc:
            print(ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

        try:
            django_args = ["migrate"]
            django_kwargs = {}
            django.core.management.call_command(*django_args, **django_kwargs)
        except django.core.management.base.CommandError, exc:
            print(ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

        print(CREATED_NEW_GAMEDIR.format(gamedir=args.init[0],
                                         settings_path=os.path.join(args.init[0], SETTINGS_PATH)))
        sys.exit()
    elif args.upgrade:
        try:
            from muddery.server.upgrader.upgrade_handler import UPGRADE_HANDLER

            game_name = args.upgrade[0]
            gamedir = os.path.abspath(os.path.join(CURRENT_DIR, game_name))

            UPGRADE_HANDLER.upgrade(gamedir)
            print(UPGRADED_GAMEDIR.format(gamedir=args.upgrade[0],
                                          version=MUDDERY_VERSION))
        except Exception, e:
            print("Upgrade failed: %s" % e)

        sys.exit()

    if args.show_version:
        # show the version info
        print(show_version_info(option == "help"))
        sys.exit()

    if args.altsettings:
        evennia_launcher.main()

    if option != "noop":
        # pass-through to evennia
        evennia_launcher.main()
    else:
        # no input; print muddery info
        print(ABOUT_INFO)


if __name__ == '__main__':
    # start Muddery from the command line
    main()
