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
    def update(self, settings):
        """
        Update configs with another Configs object.
        """
        for name in settings.__class__.__dict__:
            if name[0] != "_":
                setattr(self, name, getattr(settings, name))


    ######################################################################
    # Muddery base server config
    ######################################################################

    # This is the name of your server.
    GAME_SERVERNAME = "Muddery"

    MUDDERY_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GAME_DIR = os.getcwd()

    # Place to put log files
    LOG_DIR = os.path.join(GAME_DIR, "server", "logs")
    LOG_NAME = 'server.log'
    LOG_LEVEL = logging.INFO

    # How long time (in seconds) a user may idle before being logged
    # out. This can be set as big as desired. A user may avoid being
    # thrown off by sending the empty system command 'idle' to the server
    # at regular intervals. Set <=0 to deactivate idle timeout completely.
    IDLE_TIMEOUT = 60

    # Determine how many commands per second a given Session is allowed
    # to send to the Portal via a connected protocol. Too high rate will
    # drop the command and echo a warning. Note that this will also cap
    # OOB messages so don't set it too low if you expect a lot of events
    # from the client! To turn the limiter off, set to <= 0.
    MAX_COMMAND_RATE = 20

    # The maximum number of characters allowed by the default.
    MAX_PLAYER_CHARACTERS = 5

    # Language code for this installation. All choices can be found here:
    # http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
    LANGUAGE_CODE = "en-US"


    ######################################################################
    # Database config
    ######################################################################

    # Database config syntax:
    # ENGINE - path to the the database backend. Possible choices are:
    #            'django.db.backends.sqlite3', (default)
    #            'django.db.backends.mysql',
    #            'django.db.backends.postgresql_psycopg2' (see Issue 241),
    #            'django.db.backends.oracle' (untested).
    # NAME - database name, or path to the db file for sqlite3
    # USER - db admin (unused in sqlite3)
    # PASSWORD - db admin password (unused in sqlite3)
    # HOST - empty string is localhost (unused in sqlite3)
    # PORT - empty string defaults to localhost (unused in sqlite3)
    AL_DATABASES = {
        'gamedata': {
            'ENGINE': 'sqlite3',
            'MODELS': 'gamedata.models',
            'NAME': os.path.join(GAME_DIR, "server", "gamedata.db3"),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            'DEBUG': True,
        },
        'worlddata': {
            'ENGINE': 'sqlite3',
            'MODELS': 'worlddata.models',
            'NAME': os.path.join(GAME_DIR, "server", "worlddata.db3"),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            'DEBUG': True,
        },
    }

    # Database Access Object
    # DATABASE_ACCESS_OBJECT = 'muddery.server.database.storage.kv_table_write_back.KeyValueWriteBackTable'
    DATABASE_ACCESS_OBJECT = 'muddery.server.database.storage.kv_table.KeyValueTable'

    # Database Access Object without cache
    # DATABASE_ACCESS_OBJECT_NO_CACHE = 'muddery.server.database.storage.kv_table.KeyValueTable'
    DATABASE_ACCESS_OBJECT_NO_CACHE = 'muddery.server.database.storage.kv_table.KeyValueTable'


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
    # Muddery additional data features
    ######################################################################

    # data app name
    GAME_DATA_APP = "gamedata"

    # game data model's filename
    GAME_DATA_MODEL_FILE = "gamedata.models"

    # data app name
    WORLD_DATA_APP = "worlddata"

    # world data model's filename
    WORLD_DATA_MODEL_FILE = "worlddata.models"

    # wsgi setting
    WSGI_APPLICATION = 'muddery.server.service.router.wsgi_application'

    # websocket setting
    ASGI_APPLICATION = 'muddery.server.service.router.asgi_application'

    # data file's folder under user's game directory.
    WORLD_DATA_FOLDER = os.path.join("worlddata", "data")


    ######################################################################
    # World data features
    ######################################################################

    # add data app
    # INSTALLED_APPS = INSTALLED_APPS + [WORLD_EDITOR_APP, ]

    # Localized string data's folder.
    LOCALIZED_STRINGS_FOLDER = "languages"

    # Localized string model's name
    LOCALIZED_STRINGS_MODEL = "localized_strings"



    ###################################
    # permissions
    ###################################
    # Characters who have these permission can bypass events.
    PERMISSION_BYPASS_EVENTS = {"builders", "wizards", "immortals"}

    # Characters who have these permission can use text commands.
    PERMISSION_COMMANDS = {"playerhelpers", "builders", "wizards", "immortals"}


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
