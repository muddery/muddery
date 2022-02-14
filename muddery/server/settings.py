"""
Master configuration file for Muddery.

NOTE: NO MODIFICATIONS SHOULD BE MADE TO THIS FILE!

All settings changes should be done by copy-pasting the variable and
its value to <gamedir>/conf/settings.py.

Hint: Don't copy&paste over more from this file than you actually want
to change.  Anything you don't copy&paste will thus retain its default
value - which may change as Muddery is developed. This way you can
always be sure of what you have changed and what is default behaviour.

"""

import os
import logging


class Settings(object):
    """
    Game server's default settings.
    """

    def update(self, settings):
        """
        Update configs with another Configs object.
        """
        for name in settings.__class__.__dict__:
            if name[0] != "_":
                setattr(self, name, getattr(settings, name))

    ######################################################################
    # Base server config
    ######################################################################

    # This is a security setting protecting against host poisoning
    # attacks.  It defaults to allowing all. In production, make
    # sure to change this to your actual host addresses/IPs.
    ALLOWED_HOST = "0.0.0.0"

    # The webserver sits behind a Portal proxy.
    WEBCLIENT_PORT = 8000

    # Server-side websocket port to open for the webclient.
    WEBSERVER_PORT = 8001

    # The secret key of jwt.
    WORLD_EDITOR_SECRET = "SET_YOUR_SECRET_KEY"

    ######################################################################
    # Muddery base server config
    ######################################################################

    # Set test mode.
    TEST_MODE = False

    # This is the name of your server.
    GAME_SERVERNAME = "Muddery"

    MUDDERY_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GAME_DIR = os.getcwd()

    # Server's pid file
    SERVER_PID = os.path.join(GAME_DIR, "server.pid")

    # Webclient's pid file
    WEBCLIENT_PID = os.path.join(GAME_DIR, "webclient.pid")

    # Place to put log files
    LOG_DIR = os.path.join(GAME_DIR, "server", "logs")
    LOG_NAME = 'server.log'
    LOG_LEVEL = logging.INFO

    # The maximum number of characters allowed by the default.
    MAX_PLAYER_CHARACTERS = 5

    # Language code for this installation. All choices can be found here:
    # http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
    LANGUAGE_CODE = "en-US"

    ######################################################################
    # Database config
    # ENGINE: Database's engine. Possible choices are:
    #         'sqlite3'
    #         'mysql'
    # NAME - database name, or path to the db file for sqlite3
    # USER - db admin (unused in sqlite3)
    # PASSWORD - db admin password (unused in sqlite3)
    # HOST - empty string is localhost (unused in sqlite3)
    # PORT - empty string defaults to localhost (unused in sqlite3)
    ######################################################################
    GAMEDATA_DB = {
        'MODELS': 'gamedata.models',
        'ENGINE': 'sqlite3',
        'NAME': os.path.join(GAME_DIR, "server", "gamedata.db3"),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'DEBUG': False,
    }

    WORLDDATA_DB = {
        'MODELS': 'worlddata.models',
        'ENGINE': 'sqlite3',
        'NAME': os.path.join(GAME_DIR, "server", "worlddata.db3"),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'DEBUG': False,
    }

    # Database Access Object
    DATABASE_STORAGE_OBJECT = 'muddery.server.database.storage.table_kv_storage.TableKVStorage'

    # Database Access Object without cache
    DATABASE_CACHE_OBJECT = 'muddery.server.database.storage.memory_kv_storage.MemoryKVStorage'

    ######################################################################
    # Web features
    ######################################################################

    # Webclient files root dir.
    WEBCLIENT_ROOT = os.path.join(GAME_DIR, "web", "webclient")

    # Directories from which static files will be gathered from.
    WEBCLIENT_SOURCE_DIRS = (
        (WEBCLIENT_ROOT, os.path.join(MUDDERY_DIR, "webclient")),
        (WEBCLIENT_ROOT, os.path.join(GAME_DIR, "web", "webclient_overrides", "webclient")),
    )

    # Media files root dir
    MEDIA_ROOT = os.path.join(GAME_DIR, "web", "media")

    # resource's location
    IMAGE_PATH = 'image'

    ######################################################################
    # Typeclasses and other paths
    ######################################################################

    # Element type for accounts.
    ACCOUNT_ELEMENT_TYPE = "ACCOUNT"

    # Element type for general characters, include NPCs, mobs and player characters.
    CHARACTER_ELEMENT_TYPE = "CHARACTER"

    # Element type for player characters.
    PLAYER_CHARACTER_ELEMENT_TYPE = "PLAYER_CHARACTER"

    # Element type for player characters in test mode.
    PLAYER_CHARACTER_TYPE_TEST_MODE = "TESTER_CHARACTER"

    # Element key for player characters in test mode.
    PLAYER_CHARACTER_KEY_TEST_MODE = "tester"

    # Element type for player characters.
    STAFF_CHARACTER_ELEMENT_TYPE = "STAFF_CHARACTER"

    # Element type for rooms.
    ROOM_ELEMENT_TYPE = "ROOM"

    # Element type for Exit objects.
    EXIT_ELEMENT_TYPE = "EXIT"

    # Typeclass for Scripts (fallback). You usually don't need to change this
    # but create custom variations of scripts on a per-case basis instead.
    SCRIPT_ELEMENT_TYPE = "SCRIPT"

    # Path of base elements.
    PATH_ELEMENTS_BASE = "muddery.server.elements"

    # Path of custom elements.
    PATH_ELEMENTS_CUSTOM = "elements"

    # Game data dao's path.
    PATH_GAMEDATA_DAO = "muddery.server.database.gamedata"

    # Path of base event actions.
    PATH_EVENT_ACTION_BASE = "muddery.server.events.event_actions"

    # Path of base quest status.
    PATH_QUEST_STATUS_BASE = "muddery.server.quests.quest_status"


    ######################################################################
    # Default statement sets
    ######################################################################

    # Action functions set
    ACTION_FUNC_SET = "muddery.server.statements.default_statement_func_set.ActionFuncSet"

    # Condition functions set
    CONDITION_FUNC_SET = "muddery.server.statements.default_statement_func_set.ConditionFuncSet"

    # Skill functions set
    SKILL_FUNC_SET = "muddery.server.statements.default_statement_func_set.SkillFuncSet"


    ######################################################################
    # Default command sets
    ######################################################################
    # Command set used on the logged-in session
    SESSION_CMDSET = "muddery.server.commands.default_cmdsets.SessionCmdSet"

    # Command set for accounts without a character (ooc)
    ACCOUNT_CMDSET = "muddery.server.commands.default_cmdsets.AccountCmdSet"

    # Default set for logged in player with characters (fallback)
    CHARACTER_CMDSET = "muddery.server.commands.default_cmdsets.CharacterCmdSet"


    ######################################################################
    # World data features
    ######################################################################
    # data file's folder under user's game directory.
    WORLD_DATA_FOLDER = os.path.join("worlddata", "data")

    # Localized string data's folder.
    LOCALIZED_STRINGS_FOLDER = "languages"

    # Localized string model's name
    LOCALIZED_STRINGS_MODEL = "localized_strings"


    ###################################
    # combat settings
    ###################################
    # Handler of the combat
    NORMAL_COMBAT_HANDLER = "muddery.server.combat.combat_runner.normal_combat.NormalCombat"

    HONOUR_COMBAT_HANDLER = "muddery.server.combat.combat_runner.honour_combat.HonourCombat"

    #HONOUR_COMBAT_HANDLER = "muddery.server.combat.honour_auto_combat_handler.HonourAutoCombatHandler"

    AUTO_COMBAT_TIMEOUT = 60


    ###################################
    # AI modules
    ###################################
    AI_CHOOSE_SKILL = "muddery.server.ai.choose_skill.ChooseSkill"


SETTINGS = Settings()
