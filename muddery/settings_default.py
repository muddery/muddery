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
from evennia.settings_default import WEBSITE_TEMPLATE, WEBCLIENT_TEMPLATE
from evennia.settings_default import INSTALLED_APPS


######################################################################
# Muddery base server config
######################################################################

MUDDERY_DIR = os.path.dirname(os.path.abspath(__file__))

# Place to put log files
LOG_DIR = os.path.join(GAME_DIR, "server", "logs")
SERVER_LOG_FILE = os.path.join(LOG_DIR, 'server.log')
PORTAL_LOG_FILE = os.path.join(LOG_DIR, 'portal.log')
HTTP_LOG_FILE = os.path.join(LOG_DIR, 'http_requests.log')

# This setting is no use any more, so set it to blank.
WEBSOCKET_CLIENT_URL = ""


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
        }}


######################################################################
# Evennia base server config
######################################################################
# Activate telnet service
TELNET_ENABLED = False


######################################################################
# Django web features
######################################################################

# Context processors define context variables, generally for the template
# system to use.
TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.i18n',
                               'django.core.context_processors.request',
                               'django.contrib.auth.context_processors.auth',
                               'django.core.context_processors.media',
                               'django.core.context_processors.debug',
                               'muddery.web.utils.general_context.general_context',)

# Absolute path to the directory that holds file uploads from web apps.
# Example: "/home/media/media.lawrence.com"
MEDIA_ROOT = os.path.join(GAME_DIR, "web", "media")

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

# image resource's dir
IMAGE_RESOURCE_DIR = 'resource/image'

# icon resource's dir
ICON_RESOURCE_DIR = 'resource/icon'

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
    os.path.join(MUDDERY_DIR, "web", "website", "static"),
    os.path.join(MUDDERY_DIR, "web", "webclient", "static"),)

# We setup the location of the website template as well as the admin site.
TEMPLATES = [{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(GAME_DIR, "worlddata", "editor", "templates"),
            os.path.join(MUDDERY_DIR, "worlddata", "editor", "templates"),
            os.path.join(GAME_DIR, "web", "template_overrides", WEBSITE_TEMPLATE),
            os.path.join(GAME_DIR, "web", "template_overrides", WEBCLIENT_TEMPLATE),
            os.path.join(GAME_DIR, "web", "template_overrides"),
            os.path.join(MUDDERY_DIR, "web", "website", "templates", WEBSITE_TEMPLATE),
            os.path.join(MUDDERY_DIR, "web", "website", "templates"),
            os.path.join(MUDDERY_DIR, "web", "webclient", "templates", WEBCLIENT_TEMPLATE),
            os.path.join(MUDDERY_DIR, "web", "webclient", "templates"),
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
                'muddery.web.utils.general_context.general_context']
            }
        }]


######################################################################
# Evennia pluggable modules
######################################################################

# The command parser module to use. See the default module for which
# functions it must implement
COMMAND_PARSER = "muddery.server.conf.cmdparser.cmdparser"


######################################################################
# Typeclasses and other paths
######################################################################

# Server-side session class used.
SERVER_SESSION_CLASS = "muddery.server.conf.serversession.ServerSession"

# These are paths that will be prefixed to the paths given if the
# immediately entered path fail to find a typeclass. It allows for
# shorter input strings. They must either base off the game directory
# or start from the evennia library.
TYPECLASS_PATHS = ["muddery.typeclasses"]

# Typeclass for player objects (linked to a character) (fallback)
BASE_PLAYER_TYPECLASS = "muddery.typeclasses.players.MudderyPlayer"

# Typeclass and base for all objects (fallback)
BASE_OBJECT_TYPECLASS = "muddery.typeclasses.objects.MudderyObject"

# Typeclass for character objects linked to a player (fallback)
BASE_CHARACTER_TYPECLASS = "muddery.typeclasses.player_characters.MudderyPlayerCharacter"

# Typeclass for rooms (fallback)
BASE_ROOM_TYPECLASS = "muddery.typeclasses.rooms.MudderyRoom"

# Typeclass for Exit objects (fallback).
BASE_EXIT_TYPECLASS = "muddery.typeclasses.exits.MudderyExit"

# Typeclass for Channel (fallback).
BASE_CHANNEL_TYPECLASS = "muddery.typeclasses.channels.MudderyChannel"

# Typeclass for Scripts (fallback). You usually don't need to change this
# but create custom variations of scripts on a per-case basis instead.
BASE_SCRIPT_TYPECLASS = "muddery.typeclasses.scripts.MudderyScript"

# Typeclass for general characters, include NPCs, mobs and player characters.
BASE_GENERAL_CHARACTER_TYPECLASS = "muddery.typeclasses.characters.MudderyCharacter"


######################################################################
# Default statement sets
######################################################################

# Action functions set
ACTION_FUNC_SET = "muddery.statements.default_statement_func_set.ActionFuncSet"

# Condition functions set
CONDITION_FUNC_SET = "muddery.statements.default_statement_func_set.ConditionFuncSet"

# Skill functions set
SKILL_FUNC_SET = "muddery.statements.default_statement_func_set.SkillFuncSet"

# Handler of the combat
COMBAT_HANDLER = "muddery.typeclasses.combat_handler.MudderyCombatHandler"


######################################################################
# Default command sets
######################################################################

# Command set used on session before player has logged in
CMDSET_UNLOGGEDIN = "muddery.commands.default_cmdsets.UnloggedinCmdSet"

# Command set used on the logged-in session
CMDSET_SESSION = "muddery.commands.default_cmdsets.SessionCmdSet"

# Default set for logged in player with characters (fallback)
CMDSET_CHARACTER = "muddery.commands.default_cmdsets.CharacterCmdSet"

# Command set for players without a character (ooc)
CMDSET_PLAYER = "muddery.commands.default_cmdsets.PlayerCmdSet"

# Command set for players in combat
CMDSET_COMBAT = "muddery.commands.default_cmdsets.CombatCmdSet"


######################################################################
# World data features
######################################################################

# attribute's category for data info
DATA_KEY_CATEGORY = "data_key"

# data app name
WORLD_DATA_APP = "worlddata"

# add data app
INSTALLED_APPS = INSTALLED_APPS + (WORLD_DATA_APP,)

# data file's folder under user's game directory.
WORLD_DATA_FOLDER = os.path.join("worlddata", "data")

# game settings
GAME_SETTINGS = "game_settings"

# webclient settings
CLIENT_SETTINGS = "client_settings"

# Two way exit's typeclass key.
TWO_WAY_EXIT_TYPECLASS_KEY = "CLASS_TWO_WAY_EXIT"

# Reverse exit's typeclass path.
REVERSE_EXIT_TYPECLASS_PATH = "muddery.typeclasses.exits.MudderyReverseExit"

# Reverse exit's key's prefix.
REVERSE_EXIT_PREFIX = "__reverse__"


###################################
# Basic data
###################################

# class's categories
CLASS_CATEGORIES = "class_categories"

# typeclasses
TYPECLASSES = "typeclasses"

# equip types
EQUIPMENT_TYPES = "equipment_types"

# equipment positions
EQUIPMENT_POSITIONS = "equipment_positions"

# character's careers
CHARACTER_CAREERS = "character_careers"

# career equipments
CAREER_EQUIPMENTS = "career_equipments"

# character levels
CHARACTER_MODELS = "character_models"

# event types
EVENT_TYPES = "event_types"

# event trigger types
EVENT_TRIGGER_TYPES = "event_trigger_types"

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


###################################
# Object data
###################################

# unique rooms
WORLD_ROOMS = "world_rooms"

# unique exits
WORLD_EXITS = "world_exits"

# unique objects
WORLD_OBJECTS = "world_objects"

# unique npcs
WORLD_NPCS = "world_npcs"

# common objects
COMMON_OBJECTS = ("common_objects",
                  "common_characters",
                  "skills",
                  "quests",
                  "equipments",
                  "foods",
                  "skill_books",
                  "shops")

# all object data models
OBJECT_DATA_MODELS = (WORLD_ROOMS,
                      WORLD_EXITS,
                      WORLD_OBJECTS,
                      WORLD_NPCS) + COMMON_OBJECTS

# object's additional data
OBJECT_ADDITIONAL_DATA = ("exit_locks", "two_way_exits", "object_creators")


###################################
# other data
###################################

# loot lists
CREATOR_LOOT_LIST = "creator_loot_list"
CHARACTER_LOOT_LIST = "character_loot_list"
QUEST_REWARD_LIST = "quest_reward_list"

# quest data
QUEST_OBJECTIVE_TYPES = "quest_objective_types"
QUEST_OBJECTIVES = "quest_objectives"
QUEST_DEPENDENCY_TYPES = "quest_dependency_types"
QUEST_DEPENDENCIES = "quest_dependencies"

# event data
EVENT_DATA = "event_data"

# Event additional data. One event can have one additional data model.
EVENT_ADDITIONAL_DATA = ("event_attacks", "event_dialogues")

# dialogues
DIALOGUES = "dialogues"
DIALOGUE_SENTENCES = "dialogue_sentences"
DIALOGUE_RELATIONS = "dialogue_relations"
NPC_DIALOGUES = "npc_dialogues"
DIALOGUE_QUEST_DEPENDENCIES = "dialogue_quest_dependencies"

# character's default objects
DEFAULT_OBJECTS = "default_objects"

# character skills
DEFAULT_SKILLS = "default_skills"

# shops
SHOP_GOODS = "shop_goods"
NPC_SHOPS = "npc_shops"

# resources
IMAGE_RESOURCES = "image_resources"
ICON_RESOURCES = "icon_resources"

# custom localized string
CUSTOM_LOCALIZED_STRINGS = "custom_localized_strings"

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
                     EQUIPMENT_TYPES,
                     DEFAULT_OBJECTS,
                     DEFAULT_SKILLS,
                     SHOP_GOODS,
                     NPC_SHOPS,
                     IMAGE_RESOURCES,
                     ICON_RESOURCES,
                     CUSTOM_LOCALIZED_STRINGS,
                     GAME_SETTINGS,
                     CLIENT_SETTINGS) + OBJECT_ADDITIONAL_DATA + EVENT_ADDITIONAL_DATA

# system local strings
SYSTEM_LOCALIZED_STRINGS = "system_localized_strings"
SYSTEM_LOCALIZED_STRINGS_FOLDER = "languages"

EQUIP_EFFECTS = []

# all skill modules
SKILL_MODULES = ("skills.skills",)

# Characters who have equal or higher permission can bypass events.
PERMISSION_BYPASS_EVENTS = {"Builders", "Wizards", "Immortals"}


###################################
# world editor
###################################
DEFUALT_LIST_TEMPLATE = "common_list.html"

DEFUALT_FORM_TEMPLATE = "common_form.html"
