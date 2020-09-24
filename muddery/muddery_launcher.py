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

import sys
import argparse
from argparse import ArgumentParser
from muddery.launcher import configs


def check_main_dependencies():
    """
    Check Muddery's main dependencies.

    :return:
    """
    # add evennia's path
    sys.path.insert(1, configs.EVENNIA_LIB)
    from evennia.server import evennia_launcher
    evennia_launcher.check_main_evennia_dependencies()


def main():
    """
    Run the muddery main program.
    """

    # set up argument parser

    parser = ArgumentParser(description=configs.CMDLINE_HELP, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '--init',
        nargs='+',
        action='store',
        dest="init",
        metavar="<gamename> [template name]",
        help="creates a new gamedir 'name' at current location (from optional template).")
    parser.add_argument(
        '--log', '-l',
        action='store_true',
        dest='tail_log',
        default=False,
        help="tail the portal and server logfiles and print to stdout")
    parser.add_argument(
        '-v', '--version', action='store_true',
        dest='show_version', default=False,
        help="show version info")
    parser.add_argument(
        '--upgrade', nargs='?', const='', dest='upgrade', metavar="[template]",
        help="Upgrade a game directory 'game_name' to the latest version.")
    parser.add_argument(
        '--loaddata', action='store_true', dest='loaddata', default=False,
        help="Load local data from the worlddata folder.")
    parser.add_argument(
        '--sysdata', action='store_true', dest='sysdata', default=False,
        help="Load system default data.")
    parser.add_argument(
        '--migrate', action='store_true', dest='migrate', default=False,
        help="Migrate databases to new version.")
    parser.add_argument(
        '--port', '-p', nargs=1, action='store', dest='port',
        metavar="<N>",
        help="Set game's network ports when init the game, recommend to use ports above 10000.")
    parser.add_argument(
        "operation", nargs='?', default="noop",
        help=configs.ARG_OPTIONS)
    parser.epilog = (
        "Common Django-admin commands are shell, dbshell, test and migrate.\n"
        "See the Django documentation for more management commands.")

    args, unknown_args = parser.parse_known_args()

    # handle arguments
    option = args.operation

    # make sure we have everything
    check_main_dependencies()
    from muddery.launcher import manager

    if not args:
        # show help pane
        manager.print_help()
        sys.exit()

    elif args.init:
        # initialization of game directory
        game_name = args.init[0]

        template = None
        if len(args.init) > 1:
            template = args.init[1]

        port = None
        if args.port:
            try:
                port = int(args.port[0])
            except:
                print("Port must be a number.")
                sys.exit(-1)

        try:
            manager.init_game(game_name, template, port)
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit()

    elif args.upgrade is not None:
        template = None
        if args.upgrade:
            template = args.upgrade

        try:
            manager.upgrade_game(template)
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit()

    elif args.loaddata:
        try:
            manager.load_game_data()
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit()

    elif args.sysdata:
        try:
            manager.load_system_data()
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit()

    elif args.migrate:
        try:
            manager.migrate_database()
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit()

    if args.show_version:
        # show the version info
        manager.show_version(option == "help")
        sys.exit()

    if option != "noop":
        try:
            manager.run_evennia(option)
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit()
    else:
        # no input; print muddery info
        manager.print_about()
        sys.exit()


if __name__ == '__main__':
    # start Muddery from the command line
    main()
