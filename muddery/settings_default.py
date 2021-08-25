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
from evennia.settings_default import EVENNIA_DIR, GAME_DIR
from evennia.settings_default import WEBSITE_TEMPLATE
from evennia.settings_default import INSTALLED_APPS

######################################################################
# Muddery base server config
######################################################################

# This is the name of your server.
GAME_SERVERNAME = "Muddery"

MUDDERY_DIR = os.path.dirname(os.path.abspath(__file__))

# Place to put log files
LOG_DIR = os.path.join(GAME_DIR, "server", "logs")
SERVER_LOG_FILE = os.path.join(LOG_DIR, 'server.log')
PORTAL_LOG_FILE = os.path.join(LOG_DIR, 'portal.log')
HTTP_LOG_FILE = os.path.join(LOG_DIR, 'http_requests.log')

# This setting is no use any more, so set it to blank.
WEBSOCKET_CLIENT_URL = ""

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

######################################################################
# Evennia Database config
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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(GAME_DIR, "server", "muddery.db3"),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    },
    'gamedata': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(GAME_DIR, "server", "gamedata.db3"),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'timeout': 20,      # solve the sqlite's problem of database is locked.
        }
    },
    'worlddata': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(GAME_DIR, "server", "worlddata.db3"),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}

# Database's router
DATABASE_ROUTERS = ['muddery.server.database.database_router.DatabaseAppsRouter']

DATABASE_APPS_MAPPING = {
    'gamedata': 'gamedata',
    'worlddata': 'worlddata',
}

# Database Access Object
DATABASE_ACCESS_OBJECT = 'muddery.server.database.storage.kv_table_write_back.KeyValueWriteBackTable'

# Object's default runtime table. If a typeclass's own runtime table does
# not exist, will use this table instead.
DEFAULT_OBJECT_RUNTIME_TABLE = "object_attributes"

# Cache all Attributes, Tags, Nicks, Aliases.
TYPECLASS_FULL_CACHE = True

######################################################################
# Evennia pluggable modules
######################################################################
# Plugin modules extend Evennia in various ways. In the cases with no
# existing default, there are examples of many of these modules
# in contrib/examples.

# The command parser module to use. See the default module for which
# functions it must implement
COMMAND_PARSER = "muddery.server.conf.cmdparser.cmdparser"

# An optional module that, if existing, must hold a function
# named at_initial_setup(). This hook method can be used to customize
# the server's initial setup sequence (the very first startup of the system).
# The check will fail quietly if module doesn't exist or fails to load.
AT_INITIAL_SETUP_HOOK_MODULE = "muddery.server.conf.at_initial_setup"

# Module containing your custom at_server_start(), at_server_reload() and
# at_server_stop() methods. These methods will be called every time
# the server starts, reloads and resets/stops respectively.
AT_SERVER_STARTSTOP_MODULE = "muddery.server.conf.at_server_startstop"

# List of one or more module paths to modules containing a function start_
# plugin_services(application). This module will be called with the main
# Evennia Server application when the Server is initiated.
# It will be called last in the startup sequence.
SERVER_SERVICES_PLUGIN_MODULES = []

# List of one or more module paths to modules containing a function
# start_plugin_services(application). This module will be called with the
# main Evennia Portal application when the Portal is initiated.
# It will be called last in the startup sequence.
PORTAL_SERVICES_PLUGIN_MODULES = []

# Module holding MSSP meta data. This is used by MUD-crawlers to determine
# what type of game you are running, how many players you have etc.
MSSP_META_MODULE = "muddery.server.conf.mssp"

# Module for web plugins.
WEB_PLUGINS_MODULE = "muddery.server.conf.web_plugins"

# Tuple of modules implementing lock functions. All callable functions
# inside these modules will be available as lock functions.
LOCK_FUNC_MODULES = ("evennia.locks.lockfuncs",)

# Module holding handlers for managing incoming data from the client. These
# will be loaded in order, meaning functions in later modules may overload
# previous ones if having the same name.
INPUT_FUNC_MODULES = ["evennia.server.inputfuncs"]

# Modules that contain prototypes for use with the spawner mechanism.
PROTOTYPE_MODULES = []

# Delay to use before sending the evennia.syscmdkeys.CMD_LOGINSTART Command
# when a new session connects (this defaults the unloggedin-look for showing
# the connection screen). The delay is useful mainly for telnet, to allow
# client/server to establish client capabilities like color/mxp etc before
# sending any text. A value of 0.3 should be enough. While a good idea, it may
# cause issues with menu-logins and autoconnects since the menu will not have
# started when the autoconnects starts sending menu commands.
# Set this to 0 to send initial data to the client when its first login.
DELAY_CMD_LOGINSTART = 0

######################################################################
# Inlinefunc
######################################################################
# Evennia supports inline function preprocessing. This allows users
# to supply inline calls on the form $func(arg, arg, ...) to do
# session-aware text formatting and manipulation on the fly. If
# disabled, such inline functions will not be parsed.
INLINEFUNC_ENABLED = False
# Only functions defined globally (and not starting with '_') in
# these modules will be considered valid inlinefuncs. The list
# is loaded from left-to-right, same-named functions will overload
INLINEFUNC_MODULES = ["evennia.utils.inlinefuncs"]


######################################################################
# Evennia base server config
######################################################################
# Activate telnet service
TELNET_ENABLED = False


######################################################################
# Django web features
######################################################################

# While DEBUG is False, show a regular server error page on the web
# stuff, email the traceback to the people in the ADMINS tuple
# below. If True, show a detailed traceback for the web
# browser to display. Note however that this will leak memory when
# active, so make sure to turn it off for a production server!
DEBUG = False

# Context processors define context variables, generally for the template
# system to use.
TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.i18n',
                               'django.core.context_processors.request',
                               'django.contrib.auth.context_processors.auth',
                               'django.core.context_processors.media',
                               'django.core.context_processors.debug',
                               'muddery.server.web.utils.general_context.general_context',)

# Absolute path to the directory that holds file uploads from web apps.
# Example: "/home/media/media.lawrence.com"
MEDIA_ROOT = os.path.join(GAME_DIR, "web", "media")

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

# resource's location
IMAGE_PATH = 'image'

# The master urlconf file that contains all of the sub-branches to the
# applications. Change this to add your own URLs to the website.
ROOT_URLCONF = 'web.urls'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure
# to use a trailing slash. Django1.4+ will look for admin files under
# STATIC_URL/admin.
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(GAME_DIR, "web", "static")

# URL that handles the webclient.
WEBCLIENT_ROOT = os.path.join(GAME_DIR, "web", "static", "webclient")

# URL that handles the worldeditor.
WORLDEDITOR_ROOT = os.path.join(GAME_DIR, "web", "static", "editor")

# Directories from which static files will be gathered from.
STATICFILES_DIRS = (
    os.path.join(GAME_DIR, "web", "static_overrides"),
    os.path.join(MUDDERY_DIR, "server", "web", "website", "static"),
    ("webclient", os.path.join(GAME_DIR, "web", "webclient_overrides", "webclient")),
    ("webclient", os.path.join(MUDDERY_DIR, "webclient")),
    ("editor", os.path.join(GAME_DIR, "worldeditor", "webclient")),
    ("editor", os.path.join(MUDDERY_DIR, "worldeditor", "webclient")),
)

# We setup the location of the website template as well as the admin site.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(GAME_DIR, "web", "template_overrides", WEBSITE_TEMPLATE),
            os.path.join(GAME_DIR, "web", "template_overrides"),
            os.path.join(MUDDERY_DIR, "server", "web", "website", "templates", WEBSITE_TEMPLATE),
            os.path.join(MUDDERY_DIR, "server", "web", "website", "templates"),
            os.path.join(EVENNIA_DIR, "web", "website", "templates", WEBSITE_TEMPLATE),
            os.path.join(EVENNIA_DIR, "web", "website", "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            "context_processors": [
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.media',
                'django.template.context_processors.debug',
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                'muddery.server.web.utils.general_context.general_context',
            ],
            # While true, show "pretty" error messages for template syntax errors.
            "debug": DEBUG,
        },
    }
]


######################################################################
# Typeclasses and other paths
######################################################################

# Server-side session class used.
SERVER_SESSION_CLASS = "muddery.server.conf.serversession.ServerSession"

# These are paths that will be prefixed to the paths given if the
# immediately entered path fail to find a typeclass. It allows for
# shorter input strings. They must either base off the game directory
# or start from the evennia library.
TYPECLASS_PATHS = ["muddery.server.elements"]

# Typeclass for account objects (linked to a character) (fallback)
BASE_ACCOUNT_TYPECLASS = "muddery.server.typeclasses.accounts.MudderyAccount"

# Typeclass for guest account objects (linked to a character)
BASE_GUEST_TYPECLASS = "muddery.server.typeclasses.accounts.Guest"

# Typeclass and base for all objects (fallback)
BASE_OBJECT_TYPECLASS = "evennia.objects.objects.DefaultObject"

# Typeclass for character objects linked to a player (fallback)
BASE_CHARACTER_TYPECLASS = "evennia.objects.objects.DefaultCharacter"

# Typeclass for rooms (fallback)
BASE_ROOM_TYPECLASS = "evennia.objects.objects.DefaultRoom"

# Typeclass for Exit objects (fallback).
BASE_EXIT_TYPECLASS = "evennia.objects.objects.DefaultExit"

# Typeclass for Channel (fallback).
BASE_CHANNEL_TYPECLASS = "muddery.server.typeclasses.channels.MudderyChannel"

# Typeclass for Scripts (fallback). You usually don't need to change this
# but create custom variations of scripts on a per-case basis instead.
BASE_SCRIPT_TYPECLASS = "evennia.scripts.scripts.DefaultScript"

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

# Path of base world data forms.
PATH_DATA_FORMS_BASE = "muddery.worldeditor.forms"

# Path of base request processers.
PATH_REQUEST_PROCESSERS_BASE = "muddery.worldeditor.controllers"

# Path of base elements.
PATH_ELEMENTS_BASE = "muddery.server.elements"

# Path of custom elements.
PATH_ELEMENTS_CUSTOM = "elements"

# Path of base event actions.
PATH_EVENT_ACTION_BASE = "muddery.server.events.event_actions"

# Path of base quest status.
PATH_QUEST_STATUS_BASE = "muddery.server.quests.quest_status"


######################################################################
# Default Player setup and access
######################################################################

# Different Multisession modes allow a player (=account) to connect to the
# game simultaneously with multiple clients (=sessions). In modes 0,1 there is
# only one character created to the same name as the account at first login.
# In modes 2,3 no default character will be created and the MAX_NR_CHARACTERS
# value (below) defines how many characters the default char_create command
# allow per player.
#  0 - single session, one player, one character, when a new session is
#      connected, the old one is disconnected
#  1 - multiple sessions, one player, one character, each session getting
#      the same data
#  2 - multiple sessions, one player, many characters, one session per
#      character (disconnects multiplets)
#  3 - like mode 2, except multiple sessions can puppet one character, each
#      session getting the same data.
MULTISESSION_MODE = 2

# The maximum number of characters allowed for MULTISESSION_MODE 2,3. This is
# checked by the default ooc char-creation command. Forced to 1 for
# MULTISESSION_MODE 0 and 1.
MAX_NR_CHARACTERS = 3


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

# Command set used on session before player has logged in
CMDSET_UNLOGGEDIN = "muddery.server.commands.default_cmdsets.UnloggedinCmdSet"

# Command set used on the logged-in session
CMDSET_SESSION = "muddery.server.commands.default_cmdsets.SessionCmdSet"

# Default set for logged in player with characters (fallback)
CMDSET_CHARACTER = "muddery.server.commands.default_cmdsets.CharacterCmdSet"

# Command set for accounts without a character (ooc)
CMDSET_ACCOUNT = "muddery.server.commands.default_cmdsets.AccountCmdSet"

# Command set for players in combat
CMDSET_COMBAT = "muddery.server.commands.default_cmdsets.CombatCmdSet"


######################################################################
# Muddery additional data features
######################################################################
# data app name
GAME_DATA_APP = "gamedata"

# data app name
WORLD_DATA_APP = "worlddata"

# add data app
INSTALLED_APPS = INSTALLED_APPS + [GAME_DATA_APP, WORLD_DATA_APP]

# data file's folder under user's game directory.
WORLD_DATA_FOLDER = os.path.join("worlddata", "data")


######################################################################
# World data features
######################################################################

# data app name
WORLD_EDITOR_APP = "worldeditor"

# add data app
INSTALLED_APPS = INSTALLED_APPS + [WORLD_EDITOR_APP, ]

# Localized string data's folder.
LOCALIZED_STRINGS_FOLDER = "languages"

# Localized string model's name
LOCALIZED_STRINGS_MODEL = "localized_strings"

# World data API's url path.
WORLD_EDITOR_API_PATH = "worldeditor/api"


###################################
# permissions
###################################
# Characters who have these permission can bypass events.
PERMISSION_BYPASS_EVENTS = {"builders", "wizards", "immortals"}

# Characters who have these permission can use text commands.
PERMISSION_COMMANDS = {"playerhelpers", "builders", "wizards", "immortals"}


###################################
# world editor
###################################
DEFUALT_LIST_TEMPLATE = "common_list.html"

DEFUALT_FORM_TEMPLATE = "common_form.html"


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
