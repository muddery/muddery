# coding=utf-8

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
SERVERNAME = "决斗场"

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
LANGUAGE_CODE = 'zh-cn'

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
        'NAME': os.path.join(GAME_DIR, "server", "muddery.db3"),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
        }}}}


######################################################################
# Typeclasses and other paths
######################################################################

# Typeclass for character objects linked to a player (fallback)
BASE_CHARACTER_TYPECLASS = "typeclasses.player_characters.PlayerCharacter"


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
    os.path.join(GAME_DIR, "worlddata", "editor", "static"),
    os.path.join(MUDDERY_DIR, "worlddata", "editor", "static"),
    os.path.join(GAME_DIR, "web", "static_overrides"),
    os.path.join(MUDDERY_DIR, "web", "webclient", WEBCLIENT_TEMPLATE, "static"),
    os.path.join(MUDDERY_DIR, "web", "static"),
    os.path.join(EVENNIA_DIR, "web", "static"),)

# We setup the location of the website template as well as the admin site.
TEMPLATE_DIRS = (
    os.path.join(GAME_DIR, "worlddata", "editor", "templates"),
    os.path.join(MUDDERY_DIR, "worlddata", "editor", "templates"),
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

# add data app
INSTALLED_APPS = INSTALLED_APPS + (WORLD_DATA_APP,)

# basic data models
BASIC_DATA_MODELS = (CLASS_CATEGORIES,
                     TYPECLASSES,
                     EQUIPMENT_TYPES,
                     EQUIPMENT_POSITIONS,
                     CHARACTER_CAREERS,
                     CAREER_EQUIPMENTS,
                     CHARACTER_MODELS,
                     EVENT_TYPES,
                     EVENT_TRIGGER_TYPES)

# all object data models
OBJECT_DATA_MODELS = (WORLD_ROOMS,
                      WORLD_EXITS,
                      WORLD_OBJECTS,
                      WORLD_NPCS) + COMMON_OBJECTS + ADDITIONAL_DATA

# all other data models
OTHER_DATA_MODELS = (CREATOR_LOOT_LIST,
                     CHARACTER_LOOT_LIST,
                     QUEST_REWARD_LIST,
                     QUEST_OBJECTIVE_TYPES,
                     QUEST_OBJECTIVES,
                     QUEST_DEPENDENCY_TYPES,
                     QUEST_DEPENDENCIES,
                     EVENT_DATA,
                     DIALOGUES,
                     DIALOGUE_QUEST_DEPENDENCIES,
                     DIALOGUE_RELATIONS,
                     DIALOGUE_SENTENCES,
                     NPC_DIALOGUES,
                     CHARACTER_MODELS,
                     DEFAULT_SKILLS,
                     GAME_SETTINGS,
                     CLIENT_SETTINGS) + EVENT_ADDITIONAL_DATA

AT_INITIAL_SETUP_HOOK_MODULE = "server.conf.at_initial_setup"

EQUIP_POSITIONS = ["head", "chest", "hand", "leg"]

EQUIP_EFFECTS = ["attack", "defence"]
