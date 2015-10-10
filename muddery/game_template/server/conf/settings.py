"""
Evennia settings file.

The full options are found in the default settings file found here:

{evennia_settings_default}
{muddery_settings_default}

Note: Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

"""

# Use the defaults from Evennia unless explicitly overridden
import os
from evennia.settings_default import *
from muddery.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = {servername}

# Path to the game directory (use MUDDERY_DIR to refer to the
# core evennia library)
GAME_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# This is a security setting protecting against host poisoning
# attacks.  It defaults to allowing all. In production, make
# sure to change this to your actual host addresses/IPs.
ALLOWED_HOSTS = ["*"]

# The webserver sits behind a Portal proxy. This is a list
# of tuples (proxyport,serverport) used. The proxyports are what
# the Portal proxy presents to the world. The serverports are
# the internal ports the proxy uses to forward data to the Server-side
# webserver (these should not be publicly open)
WEBSERVER_PORTS = [(8000, 5001)]

# This setting is no use any more, so set it to blank.
WEBSOCKET_CLIENT_URL = ""

# Place to put log files
LOG_DIR = os.path.join(GAME_DIR, "server", "logs")
SERVER_LOG_FILE = os.path.join(LOG_DIR, 'server.log')
PORTAL_LOG_FILE = os.path.join(LOG_DIR, 'portal.log')
HTTP_LOG_FILE = os.path.join(LOG_DIR, 'http_requests.log')

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
LANGUAGE_CODE = 'en-us'

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
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(GAME_DIR, "server", "evennia.db3"),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
        }}}}

######################################################################
# Django web features
######################################################################

# Absolute path to the directory that holds file uploads from web apps.
# Example: "/home/media/media.lawrence.com"
MEDIA_ROOT = os.path.join(GAME_DIR, "web", "media")

# The master urlconf file that contains all of the sub-branches to the
# applications. Change this to add your own URLs to the website.
ROOT_URLCONF = 'web.urls'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure
# to use a trailing slash. Django1.4+ will look for admin files under
# STATIC_URL/admin.
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(GAME_DIR, "web", "static")

# Directories from which static files will be gathered from.
STATICFILES_DIRS = (
    os.path.join(GAME_DIR, "web", "static_overrides"),
    os.path.join(MUDDERY_DIR, "web", "webclient", WEBCLIENT_TEMPLATE, "static"),
    os.path.join(MUDDERY_DIR, "web", "static"),
    os.path.join(EVENNIA_DIR, "web", "static"),)

# We setup the location of the website template as well as the admin site.
TEMPLATE_DIRS = (
    os.path.join(GAME_DIR, "web", "template_overrides"),
    os.path.join(MUDDERY_DIR, "web", "webclient", WEBCLIENT_TEMPLATE),
    os.path.join(MUDDERY_DIR, "web", "templates"),
    os.path.join(EVENNIA_DIR, "web", "templates", ACTIVE_TEMPLATE),
    os.path.join(EVENNIA_DIR, "web", "templates"),)

# The secret key is randomly seeded upon creation. It is used to sign
# Django's cookies. Do not share this with anyone. Changing it will
# log out all active web browsing sessions. Game web client sessions
# may survive.
SECRET_KEY = {secret_key}

######################################################################
# World data features
######################################################################

# data file's encoding
WORLD_DATA_FILE_ENCODING = "utf8"

# add data app
INSTALLED_APPS = INSTALLED_APPS + (WORLD_DATA_APP,)

# all object data models
OBJECT_DATA_MODELS = (WORLD_ROOMS,
                      WORLD_EXITS,
                      WORLD_OBJECTS,
                      WORLD_NPCS,
                      COMMON_OBJECTS)

# all other data models
OTHER_DATA_MODELS = (QUEST_OBJECTIVES,
                     QUEST_DEPENDENCY,
                     EVENT_DATA,
                     EVENT_MOBS,
                     EVENT_DIALOGUES,
                     DIALOGUES,
                     DIALOGUE_SENTENCES,
                     DIALOGUE_RELATIONS,
                     NPC_DIALOGUES,
                     DIALOGUE_QUEST_DEPENDENCY,
                     EQUIPMENT_TYPES,
                     CHARACTER_LEVELS,
                     CHARACTER_SKILLS)

AT_INITIAL_SETUP_HOOK_MODULE = "server.conf.at_initial_setup"

# The default home location used for all objects. This is used as a
# fallback if an object's normal home location is deleted. It is the
# key of the room. If it is empty, the home will be set to the first
# room in WORLD_ROOMS.
DEFAULT_HOME_KEY = ""

# The start position for new characters. It is the key of the room.
# If it is empty, the home will be set to the first room in WORLD_ROOMS.
#  MULTISESSION_MODE = 0, 1 - used by default unloggedin create command
#  MULTISESSION_MODE = 2,3 - used by default character_create command
START_LOCATION_KEY = ""

EQUIP_POSITIONS = []

EQUIP_EFFECTS = []

SKILL_FOLDER = "skills"

SKILL_FILES = ["skills"]
