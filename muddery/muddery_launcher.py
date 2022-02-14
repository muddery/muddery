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
    sys_argv = sys.argv
    if len(sys_argv) <= 1:
        # no argv, show help
        print(configs.ABOUT_INFO)
        sys.exit(0)

    elif sys_argv[1] == "init":
        # initialization of game directory
        if len(sys_argv) <= 2:
            print("You should input the game directory's name.")
            sys.exit(-1)

        parser = ArgumentParser()
        parser.add_argument('-p', '--port', nargs=1, action='store', dest='port')
        args, unknown_args = parser.parse_known_args()

        game_name = sys_argv[2]
        template = None
        if len(sys_argv) >= 4:
            template = sys_argv[3]

        port = None
        if args.port:
            try:
                port = int(args.port[0])
            except:
                print("Port must be a number.")
                sys.exit(-1)

        from muddery.launcher import manager
        try:
            manager.init_game(game_name, template, port)
        except Exception as e:
            traceback.print_exc()
            sys.exit(-1)
        sys.exit(0)

    elif sys_argv[1] == "setup":
        # Create databases and load default data.
        from muddery.launcher import manager
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

    elif sys_argv[1] == "upgrade":
        # Upgrade the game dir to the latest version.
        from muddery.launcher import manager
        try:
            manager.upgrade_game()
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit(0)

    elif sys_argv[1] == "migrate":
        # Migrate databases to new version.
        from muddery.launcher import manager
        try:
            manager.migrate_database("gamedata")
            manager.migrate_database("worlddata")
            manager.migrate_database("worldeditor")
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit(0)

    elif sys_argv[1] == "loaddata":
        # Load game data from the worlddata folder.
        from muddery.launcher import manager
        try:
            manager.load_game_data()
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit(0)

    elif sys_argv[1] == "sysdata":
        # Reload system default data.
        from muddery.launcher import manager
        try:
            manager.load_system_data()
        except Exception as e:
            print(e)
            sys.exit(-1)
        sys.exit(0)

    elif sys_argv[1] == "start":
        # Start servers.
        parser = ArgumentParser()
        parser.add_argument('-s', '--server', action='store_true', dest='server', default=False)
        parser.add_argument('-c', '--client', action='store_true', dest='client', default=False)
        parser.add_argument('-e', '--editor', action='store_true', dest='editor', default=False)
        args, unknown_args = parser.parse_known_args()

        from muddery.launcher import manager
        try:
            if not args.server and not args.client and not args.editor:
                asyncio.run(manager.run_servers(server=True, webclient=True, editor=True))
            else:
                asyncio.run(manager.run_servers(
                    server=args.server,
                    webclient=args.client,
                    editor=args.editor
                ))
        except Exception as e:
            traceback.print_exc()
            sys.exit(-1)
        sys.exit(0)

    elif sys_argv[1] == "stop":
        # Stop servers.
        parser = ArgumentParser()
        parser.add_argument('-s', '--server', action='store_true', dest='server', default=False)
        parser.add_argument('-c', '--client', action='store_true', dest='client', default=False)
        parser.add_argument('-e', '--editor', action='store_true', dest='editor', default=False)
        args, unknown_args = parser.parse_known_args()

        from muddery.launcher import manager
        try:
            if not args.server and not args.client and not args.editor:
                manager.kill_servers()
            else:
                manager.kill_servers(
                    server=args.server,
                    webclient=args.client,
                    editor=args.editor
                )
        except Exception as e:
            traceback.print_exc()
            sys.exit(-1)
        sys.exit(0)

    else:
        # Other operations
        parser = ArgumentParser(add_help=False)
        parser.add_argument('-v', '--version', action='store_true', dest='show_version', default=False)
        parser.add_argument('-h', '--help', action='store_true', dest='show_help', default=False)
        args, unknown_args = parser.parse_known_args()

        from muddery.launcher import manager

        if args.show_version:
            # show the version info
            manager.show_version()
            sys.exit(0)
        elif args.show_help:
            # show the help info
            print(configs.CMDLINE_HELP)
            sys.exit(0)
        else:
            # no input; print muddery info
            print(configs.ABOUT_INFO)
            sys.exit(0)


if __name__ == '__main__':
    # start Muddery from the command line
    main()
