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

import os, sys, glob, traceback
import django.core.management
import argparse
from argparse import ArgumentParser
from muddery.launcher import configs

# add evennia's path
sys.path.insert(1, configs.EVENNIA_LIB)
from evennia.server import evennia_launcher
from muddery.launcher import utils


def import_local_data():
    """
    Import all local data files to models.
    """
    from django.conf import settings
    from muddery.worldeditor.services import importer
    from muddery.worldeditor.services.data_importer import import_file

    # load custom data
    # data file's path
    data_path = os.path.join(settings.GAME_DIR, settings.WORLD_DATA_FOLDER)
    importer.import_data_path(data_path)

    # localized string file's path
    localized_string_path = os.path.join(data_path, settings.LOCALIZED_STRINGS_FOLDER, settings.LANGUAGE_CODE)
    importer.import_table_path(localized_string_path, settings.LOCALIZED_STRINGS_MODEL)


def print_info():
    """
    Format info dicts from the Portal/Server for display

    """
    from django.conf import settings

    ind = " " * 8
    info = {
        "servername": settings.GAME_SERVERNAME,
        "version": utils.muddery_version(),
        "status": ""
    }

    def _prepare_dict(dct):
        out = {}
        for key, value in dct.items():
            if isinstance(value, list):
                value = "\n{}".format(ind).join(str(val) for val in value)
            out[key] = value
        return out

    def _strip_empty_lines(string):
        return "\n".join(line for line in string.split("\n") if line.strip())

    # Print server info.
    sdict = _prepare_dict(info)
    info = _strip_empty_lines(configs.SERVER_INFO.format(**sdict))

    maxwidth = max(len(line) for line in info.split("\n"))
    top_border = "-" * (maxwidth - 11) + " Muddery " + "---"
    border = "-" * (maxwidth + 1)
    print("\n" + top_border + "\n" + info + '\n' + border)



def main():
    """
    Run the muddery main program.
    """

    # set up argument parser

    parser = ArgumentParser(description=configs.CMDLINE_HELP, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '--gamedir', nargs=1, action='store', dest='altgamedir',
        metavar="<path>",
        help="location of gamedir (default: current location)")
    parser.add_argument(
        '--init', nargs='+', action='store', dest="init", metavar="<gamename> [template name]",
        help="creates a new gamedir 'name' at current location (from optional template).")
    parser.add_argument(
        '--log', '-l', action='store_true', dest='tail_log', default=False,
        help="tail the portal and server logfiles and print to stdout")
    parser.add_argument(
        '--list', nargs='+', action='store', dest='listsetting', metavar="all|<key>",
        help=("list settings, use 'all' to list all available keys"))
    parser.add_argument(
        '--settings', nargs=1, action='store', dest='altsettings',
        default=None, metavar="<path>",
        help=("start evennia with alternative settings file from\n"
              " gamedir/server/conf/. (default is settings.py)"))
    parser.add_argument(
        '--initsettings', action='store_true', dest="initsettings",
        default=False,
        help="create a new, empty settings file as\n gamedir/server/conf/settings.py")
    parser.add_argument(
        '--profiler', action='store_true', dest='profiler', default=False,
        help="start given server component under the Python profiler")
    parser.add_argument(
        '--dummyrunner', nargs=1, action='store', dest='dummyrunner',
        metavar="<N>",
        help="test a server by connecting <N> dummy accounts to it")
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
        "operation", nargs='?', default="noop",
        help=configs.ARG_OPTIONS)
    parser.epilog = (
        "Common Django-admin commands are shell, dbshell, test and migrate.\n"
        "See the Django documentation for more management commands.")

    args, unknown_args = parser.parse_known_args()

    # handle arguments
    option = args.operation

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
        evennia_launcher.GAMEDIR = gamedir
        evennia_launcher.init_game_directory(gamedir, check_db=False)

        # make migrations
        try:
            django_args = ["makemigrations", "gamedata"]
            django_kwargs = {}
            django.core.management.call_command(*django_args, **django_kwargs)
        except django.core.management.base.CommandError as exc:
            print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

        try:
            django_args = ["makemigrations", "worlddata"]
            django_kwargs = {}
            django.core.management.call_command(*django_args, **django_kwargs)
        except django.core.management.base.CommandError as exc:
            print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

        # migrate the database
        try:
            django_args = ["migrate"]
            django_kwargs = {}
            django.core.management.call_command(*django_args, **django_kwargs)

            django_args = ["migrate", "gamedata"]
            django_kwargs = {"database": "gamedata"}
            django.core.management.call_command(*django_args, **django_kwargs)

            django_args = ["migrate", "worlddata"]
            django_kwargs = {"database": "worlddata"}
            django.core.management.call_command(*django_args, **django_kwargs)
        except django.core.management.base.CommandError as exc:
            print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))
            
        # import worlddata
        try:
            print("Importing local data.")
            import_local_data()
        except Exception as e:
            traceback.print_exc()
            print("Import local data error: %s" % e)
        
        print(configs.CREATED_NEW_GAMEDIR.format(gamedir=args.init[0],
                                                 settings_path=os.path.join(args.init[0], configs.SETTINGS_PATH)))
        sys.exit()
    elif args.upgrade is not None:
        utils.check_gamedir(configs.CURRENT_DIR)

        try:
            from muddery.launcher.upgrader.upgrade_handler import UPGRADE_HANDLER
            template = None
            if args.upgrade:
                template = args.upgrade

            gamedir = os.path.abspath(configs.CURRENT_DIR)
            UPGRADE_HANDLER.upgrade_game(gamedir, template, configs.MUDDERY_LIB)
        except Exception as e:
            print("Upgrade failed: %s" % e)

        sys.exit()
    elif args.loaddata:
        print("Importing local data.")

        gamedir = os.path.abspath(configs.CURRENT_DIR)
        os.chdir(gamedir)
        evennia_launcher.init_game_directory(gamedir, check_db=False)
            
        # make migrations
        django_args = ["makemigrations", "worlddata"]
        django_kwargs = {}
        try:
            django.core.management.call_command(*django_args, **django_kwargs)
        except django.core.management.base.CommandError as exc:
            print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

        # migrate the database
        django_args = ["migrate"]
        django_kwargs = {}
        try:
            django.core.management.call_command(*django_args, **django_kwargs)
        except django.core.management.base.CommandError as exc:
            print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

        django_args = ["migrate", "worlddata"]
        django_kwargs = {"database": "worlddata"}
        try:
            django.core.management.call_command(*django_args, **django_kwargs)
        except django.core.management.base.CommandError as exc:
            print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))
            
        # load local data
        try:
            import_local_data()
            print("Import local data success.")
        except Exception as e:
            traceback.print_exc()
            print("Import local data error: %s" % e)

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

            from muddery.launcher.upgrader.upgrade_handler import UPGRADE_HANDLER
            game_ver, game_template = utils.get_game_config(configs.CURRENT_DIR)
            if UPGRADE_HANDLER.can_upgrade(game_ver):
                ver_str = ".".join([str(v) for v in game_ver])
                print(configs.NEED_UPGRADE.format(version=ver_str))
                return
        except Exception as e:
            traceback.print_exc()
            print("Check upgrade error: %s" % e)
            return

        # pass-through to evennia
        try:
            evennia_launcher.main()
        except Exception as e:
            traceback.print_exc()

        if option == "start":
            # Collect static files.
            django_args = ["collectstatic"]
            django_kwargs = {"verbosity": 0,
                             "interactive": False}
            try:
                django.core.management.call_command(*django_args, **django_kwargs)
                print("\nStatic file collected.")
            except django.core.management.base.CommandError as exc:
                print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

            print_info()
    else:
        # no input; print muddery info
        print(configs.ABOUT_INFO)


if __name__ == '__main__':
    # start Muddery from the command line
    main()
