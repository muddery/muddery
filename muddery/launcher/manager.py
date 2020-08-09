
import os
import sys
import traceback
import django.core.management
from evennia.server import evennia_launcher
from muddery.launcher import configs, utils


def print_help():
    """
    Print help messages.
    """
    print(configs.CMDLINE_HELP)


def print_about():
    """
    Print about info.

    :return:
    """
    print(configs.ABOUT_INFO)


def init_game(game_name, template=None, port=None):
    """
    Create a new game project.

    :param game_name: game project's name
    :param template: game template's name
    :param port: game server's port.
    :return:
    """
    gamedir = os.path.abspath(os.path.join(configs.CURRENT_DIR, game_name))
    utils.create_game_directory(gamedir, template, port)

    os.chdir(gamedir)
    evennia_launcher.GAMEDIR = gamedir
    evennia_launcher.init_game_directory(gamedir, check_db=False)

    try:
        utils.create_database()
    except Exception as e:
        traceback.print_exc()
        print("Create database error: %s" % e)
        return

    print(configs.CREATED_NEW_GAMEDIR.format(gamedir=game_name,
                                             settings_path=os.path.join(game_name, configs.SETTINGS_PATH),
                                             port=port if port else 8000))


def upgrade_game(template=None):
    """
    Upgrade the game project to the latest Muddery version.

    :param template: game template's name
    :return:
    """
    utils.check_gamedir(configs.CURRENT_DIR)

    try:
        from muddery.launcher.upgrader.upgrade_handler import UPGRADE_HANDLER

        gamedir = os.path.abspath(configs.CURRENT_DIR)
        UPGRADE_HANDLER.upgrade_game(gamedir, template, configs.MUDDERY_LIB)
    except Exception as e:
        print("Upgrade failed: %s" % e)


def load_game_data():
    """
    Reload the game's default data.

    :return:
    """
    print("Importing local data.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    os.chdir(gamedir)
    evennia_launcher.init_game_directory(gamedir, check_db=False)

    # load local data
    try:
        utils.import_local_data()
        print("Import local data success.")
    except Exception as e:
        traceback.print_exc()
        print("Import local data error: %s" % e)


def load_system_data():
    """
    Reload Muddery's system data.

    :return:
    """
    print("Importing system data.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    os.chdir(gamedir)
    evennia_launcher.init_game_directory(gamedir, check_db=False)

    # load local data
    try:
        utils.import_system_data()
        print("Import system data success.")
    except Exception as e:
        traceback.print_exc()
        print("Import system data error: %s" % e)


def migrate_database():
    """
    Migrate databases to the latest Muddery version.

    :return:
    """
    print("Migrating databases.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    os.chdir(gamedir)
    evennia_launcher.init_game_directory(gamedir, check_db=False)

    # make migrations
    django_args = ["makemigrations", "gamedata"]
    django_kwargs = {}
    try:
        django.core.management.call_command(*django_args, **django_kwargs)
    except django.core.management.base.CommandError as exc:
        print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))

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

    django_args = ["migrate", "gamedata"]
    django_kwargs = {"database": "gamedata"}
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


def show_version(about=False):
    """
    Show system version.

    :param about: show about info.
    :return:
    """
    print(utils.show_version_info(about))


def run_evennia(option):
    """
    Run Evennia's launcher.

    :param option: command line's option args
    :return:
    """
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

        utils.print_info()

