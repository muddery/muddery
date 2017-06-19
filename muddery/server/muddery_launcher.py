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
import django.core.management
from argparse import ArgumentParser
from muddery.server.launcher import configs

# add evennia's path
sys.path.insert(1, configs.EVENNIA_LIB)
from evennia.server import evennia_launcher
from muddery.server.launcher import utils


def main():
    """
    Run the muddery main program.
    """

    # set up argument parser

    parser = ArgumentParser(description=configs.CMDLINE_HELP)
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
    parser.add_argument('--upgrade', nargs='?', const='', dest='upgrade', metavar="[template]",
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
        print(configs.CMDLINE_HELP)
        sys.exit()
    elif args.init:
        # initialization of game directory
        game_name = args.init[0]
        template = None
        if len(args.init) > 1:
            template = args.init[1]

        gamedir = os.path.abspath(os.path.join(configs.CURRENT_DIR, game_name))
        utils.create_game_directory(gamedir, template)

        os.chdir(gamedir)
        evennia_launcher.init_game_directory(gamedir, check_db=False)

        django_args = ["makemigrations"]
        django_kwargs = {}
        try:
            django.core.management.call_command(*django_args, **django_kwargs)
        except django.core.management.base.CommandError, exc:
            print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

        try:
            django_args = ["migrate"]
            django_kwargs = {}
            django.core.management.call_command(*django_args, **django_kwargs)
        except django.core.management.base.CommandError, exc:
            print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

        print(configs.CREATED_NEW_GAMEDIR.format(gamedir=args.init[0],
                                                 settings_path=os.path.join(args.init[0], configs.SETTINGS_PATH)))
        sys.exit()
    elif args.upgrade is not None:
        utils.check_gamedir(configs.CURRENT_DIR)

        try:
            from muddery.server.upgrader.upgrade_handler import UPGRADE_HANDLER
            template = None
            if args.upgrade:
                template = args.upgrade

            gamedir = os.path.abspath(configs.CURRENT_DIR)
            UPGRADE_HANDLER.upgrade_game(gamedir, template, configs.MUDDERY_LIB)
        except Exception, e:
            print("Upgrade failed: %s" % e)

        sys.exit()

    if args.show_version:
        # show the version info
        print(utils.show_version_info(option == "help"))
        sys.exit()

    if args.altsettings:
        evennia_launcher.main()

    if option != "noop":
        # check current game's version
        try:
            utils.check_gamedir(configs.CURRENT_DIR)
            evennia_launcher.set_gamedir(configs.CURRENT_DIR)

            from muddery.server.upgrader.upgrade_handler import UPGRADE_HANDLER
            game_ver, game_template = utils.get_game_config(configs.CURRENT_DIR)
            if UPGRADE_HANDLER.can_upgrade(game_ver):
                ver_str = ".".join([str(v) for v in game_ver])
                print(configs.NEED_UPGRADE.format(version=ver_str))
                return
        except Exception, e:
            print("Check upgrade error: %s" % e)
            return

        # pass-through to evennia
        evennia_launcher.main()
    else:
        # no input; print muddery info
        print(configs.ABOUT_INFO)


if __name__ == '__main__':
    # start Muddery from the command line
    main()
