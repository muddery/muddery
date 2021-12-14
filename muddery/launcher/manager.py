
import os
import sys
import traceback
import django
import django.core.management
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
    utils.init_game_env(gamedir)

    print(configs.CREATED_NEW_GAMEDIR.format(gamedir=game_name,
                                             settings_path=os.path.join(game_name, configs.SETTINGS_PATH),
                                             port=port if port else 8000))


def upgrade_game(template=None):
    """
    Upgrade the game project to the latest Muddery version.

    :param template: game template's name
    :return:
    """
    if not utils.check_gamedir(configs.CURRENT_DIR):
        raise Exception

    from muddery.launcher.upgrader.upgrade_handler import UPGRADE_HANDLER
    gamedir = os.path.abspath(configs.CURRENT_DIR)
    UPGRADE_HANDLER.upgrade_game(gamedir, template, configs.MUDDERY_LIB)


def load_game_data():
    """
    Reload the game's default data.

    :return:
    """
    print("Importing local data.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    # load local data
    try:
        utils.import_local_data(clear=True)
        print("Import local data success.")
    except Exception as e:
        traceback.print_exc()
        raise


def load_system_data():
    """
    Reload Muddery's system data.

    :return:
    """
    print("Importing system data.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    # load system data
    try:
        utils.import_system_data()
        print("Import system data success.")
    except Exception as e:
        traceback.print_exc()
        raise


def migrate_database():
    """
    Migrate databases to the latest Muddery version.

    :return:
    """
    print("Migrating databases.")

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    try:
        from muddery.server.server import Server
        Server.instance().connect_db()
    except Exception as e:
        traceback.print_exc()
        print("Migrate database error: %s" % e)


def show_version(about=False):
    """
    Show system version.

    :param about: show about info.
    :return:
    """
    print(utils.show_version_info(about))


def create_superuser(username, password):
    """
    Create the superuser's account.
    """
    from evennia.accounts.models import AccountDB
    AccountDB.objects.create_superuser(username, '', password)


def setup_server():
    """
    Setup the server.
    """
    django.setup()

    from muddery.server.server import Server
    Server.inst().connect_db()
    Server.inst().create_the_world()
    Server.inst().create_command_handler()


def collect_static():
    """
    Collect static web files.
    :return:
    """
    gamedir = os.path.abspath(configs.CURRENT_DIR)
    utils.init_game_env(gamedir)

    django_args = ["collectstatic"]
    django_kwargs = {"verbosity": 0,
                     "interactive": False}
    try:
        django.core.management.call_command(*django_args, **django_kwargs)
        print("\nStatic file collected.")
    except django.core.management.base.CommandError as exc:
        print(configs.ERROR_INPUT.format(traceback=exc, args=django_args, kwargs=django_kwargs))


def run_evennia(option):
    """
    Run Evennia's launcher.

    :param option: command line's option args
    :return:
    """
    if not utils.check_version():
        print(configs.NEED_UPGRADE)
        raise Exception

    gamedir = os.path.abspath(configs.CURRENT_DIR)
    os.chdir(gamedir)
    evennia_launcher.init_game_directory(gamedir, check_db=False)

    if not utils.check_database():
        try:
            print("Migrating databases.")
            utils.create_database()
        except Exception as e:
            traceback.print_exc()
            print("Migrate database error: %s" % e)
            raise

        try:
            print("Importing local data.")
            utils.import_local_data()
        except Exception as e:
            traceback.print_exc()
            print("Import local data error: %s" % e)
            raise

    # pass-through to evennia
    try:
        evennia_launcher.main()
    except Exception as e:
        traceback.print_exc()
        raise

    if option == "start":
        # Collect static files.
        collect_static()

        utils.print_info()


def start(game_dir):
    """
    Start the game.
    :return:
    """
    evennia_launcher.init_game_directory(game_dir, check_db=True)
    evennia_launcher.error_check_python_modules()
    evennia_launcher.start_evennia()
