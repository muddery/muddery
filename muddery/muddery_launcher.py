#!/usr/bin/env python
"""
MUDDERY SERVER LAUNCHER SCRIPT

This is the start point for running Muddery.
"""

import traceback
import sys
import argparse
import asyncio
from argparse import ArgumentParser
from muddery.launcher import configs


def main():
    """
    Run the muddery main program.
    """
    # set up argument parser
    CMDLINE_HELP = \
        """
Starts or operates the Muddery game server.
"""

    parser = ArgumentParser(description=CMDLINE_HELP, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "operation",
        nargs='?',
        default="noop",
        help=configs.ARG_OPTIONS)
    parser.add_argument(
        '-s', '--server',
        action='store_true',
        dest='run_server',
        default=False,
        help="Run the game server only.")
    parser.add_argument(
        '-w', '--webclient',
        action='store_true',
        dest='run_webclient',
        default=False,
        help="Run the web client only.")
    parser.add_argument(
        '-e', '--editor',
        action='store_true',
        dest='run_editor',
        default=False,
        help="Run the world editor only.")
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        dest='show_version',
        default=False,
        help="show version info")
    parser.add_argument(
        '--init',
        nargs="+",
        action='store',
        dest="init",
        metavar="<dir> [template]",
        help="Creates a new gamedir 'name' at current location (from optional template).")
    parser.add_argument(
        '--setup',
        action='store_true',
        dest='setup',
        default=False,
        help="Setup a new created game dir.")
    parser.add_argument(
        '--upgrade',
        nargs='?',
        dest='upgrade',
        metavar="template",
        help="Upgrade a game directory 'game_name' to the latest version.")
    parser.add_argument(
        '--loaddata',
        action='store_true',
        dest='loaddata',
        default=False,
        help="Load local data from the worlddata folder.")
    parser.add_argument(
        '--sysdata',
        action='store_true',
        dest='sysdata',
        default=False,
        help="Load system default data.")
    parser.add_argument(
        '--migrate',
        action='store_true',
        dest='migrate',
        default=False,
        help="Migrate databases to new version.")
    parser.add_argument(
        '-p', '--port',
        nargs=1,
        action='store',
        dest='port',
        metavar="<N>",
        help="Set game's network default ports when init the game, recommend to use ports above 10000.")

    parser.epilog = (
        "")

    args, unknown_args = parser.parse_known_args()

    # handle arguments
    operation = args.operation

    # make sure we have everything
    from muddery.launcher import manager

    if not args:
        # show help pane
        manager.print_about()
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
            traceback.print_exc()
            sys.exit(-1)
        sys.exit()

    elif args.setup:
        # Create databases and load default data.
        try:
            manager.create_server_tables()
            manager.create_worldeditor_tables()
            manager.load_game_data()
            manager.collect_webclient_static()
            manager.collect_worldeditor_static()
        except Exception as e:
            traceback.print_exc()
            sys.exit(-1)
        sys.exit(0)

    elif args.upgrade:
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
            manager.migrate_database("gamedata")
            manager.migrate_database("worlddata")
            manager.migrate_database("worldeditor")
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit()

    if args.show_version:
        # show the version info
        manager.show_version()
        sys.exit()

    if operation == "start":
        try:
            if not args.run_server and not args.run_webclient and not args.run_editor:
                asyncio.run(manager.run_servers(server=True, webclient=True, editor=True))
            else:
                asyncio.run(manager.run_servers(
                    server=args.run_server,
                    webclient=args.run_webclient,
                    editor=args.run_editor
                ))
        except Exception as e:
            traceback.print_exc()
            print(e)
            sys.exit(-1)
        sys.exit()
    elif operation == "stop":
        try:
            if not args.run_server and not args.run_webclient and not args.run_editor:
                manager.kill_servers()
            else:
                manager.kill_servers(
                    server=args.run_server,
                    webclient=args.run_webclient,
                    editor=args.run_editor
                )
        except Exception as e:
            traceback.print_exc()
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
