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


######################################################################
# Muddery base server config
######################################################################

# This is the name of your server.
GAME_SERVERNAME = "Muddery"

MUDDERY_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.getcwd()

# Place to put log files
LOG_DIR = os.path.join(GAME_DIR, "server", "logs")
LOG_NAME = 'server.log'
LOG_LEVEL = logging.INFO

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

# The maximum number of characters allowed by the default.
MAX_PLAYER_CHARACTERS = 5


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

# Database's router
DATABASE_ROUTERS = ['muddery.server.database.database_router.DatabaseAppsRouter']

DATABASE_APPS_MAPPING = {
    'gamedata': 'gamedata',
    'worlddata': 'worlddata',
}

# Database Access Object
# DATABASE_ACCESS_OBJECT = 'muddery.server.database.storage.kv_table_write_back.KeyValueWriteBackTable'
DATABASE_ACCESS_OBJECT = 'muddery.server.database.storage.kv_table.KeyValueTable'

# Database Access Object without cache
# DATABASE_ACCESS_OBJECT_NO_CACHE = 'muddery.server.database.storage.kv_table.KeyValueTable'
DATABASE_ACCESS_OBJECT_NO_CACHE = 'muddery.server.database.storage.kv_table.KeyValueTable'

# Object's default runtime table. If a typeclass's own runtime table does
# not exist, will use this table instead.
DEFAULT_OBJECT_RUNTIME_TABLE = "object_attributes"

# Cache all Attributes, Tags, Nicks, Aliases.
TYPECLASS_FULL_CACHE = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


######################################################################
# Django web features
######################################################################

# While DEBUG is False, show a regular server error page on the web
# stuff, email the traceback to the people in the ADMINS tuple
# below. If True, show a detailed traceback for the web
# browser to display. Note however that this will leak memory when
# active, so make sure to turn it off for a production server!
DEBUG = False

# If using Sites/Pages from the web admin, this value must be set to the
# database-id of the Site (domain) we want to use with this game's Pages.
SITE_ID = 1

# Context processors define context variables, generally for the template
# system to use.
TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.i18n',
                               'django.core.context_processors.request',
                               'django.contrib.auth.context_processors.auth',
                               'django.core.context_processors.debug',
                               'muddery.server.web.utils.general_context.general_context',)

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
    (os.path.join("webclient", "media"), os.path.join(GAME_DIR, "web", "media")),
)

# We setup the location of the website template as well as the admin site.
WEBSITE_TEMPLATE = "website"
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(GAME_DIR, "web", "template_overrides", WEBSITE_TEMPLATE),
            os.path.join(GAME_DIR, "web", "template_overrides"),
            os.path.join(MUDDERY_DIR, "server", "web", "website", "templates", WEBSITE_TEMPLATE),
            os.path.join(MUDDERY_DIR, "server", "web", "website", "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            "context_processors": [
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.media',
                'django.template.context_processors.debug',
                "django.contrib.messages.context_processors.messages",
                'muddery.server.web.utils.general_context.general_context',
            ],
            # While true, show "pretty" error messages for template syntax errors.
            "debug": DEBUG,
        },
    }
]


# MiddleWare are semi-transparent extensions to Django's functionality.
# see http://www.djangoproject.com/documentation/middleware/ for a more detailed
# explanation.
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",  # 1.4?
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.admindocs.middleware.XViewMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
]


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

# add data app
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.flatpages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "gamedata",
    "worlddata",
]

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

######################################################################
# Django extensions
######################################################################

# Django extesions are useful third-party tools that are not
# always included in the default django distro.
try:
    import django_extensions  # noqa
    INSTALLED_APPS = INSTALLED_APPS.append("django_extensions")
except ImportError:
    # Django extensions are not installed in all distros.
    pass

# data file's folder under user's game directory.
WORLD_DATA_FOLDER = os.path.join("worlddata", "data")


######################################################################
# World data features
######################################################################

# data app name
WORLD_EDITOR_APP = "worldeditor"

# add data app
# INSTALLED_APPS = INSTALLED_APPS + [WORLD_EDITOR_APP, ]

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
