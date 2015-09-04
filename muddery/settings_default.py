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

######################################################################
# Muddery base server config
######################################################################

MUDDERY_DIR = os.path.dirname(os.path.abspath(__file__))


######################################################################
# Django web features
######################################################################

# The name of the currently selected webclient template. This corresponds to the
# directory names shown in the webtemplates directory.
WEBCLIENT_TEMPLATE = 'default'

# Context processors define context variables, generally for the template
# system to use.
TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.i18n',
                               'django.core.context_processors.request',
                               'django.contrib.auth.context_processors.auth',
                               'django.core.context_processors.media',
                               'django.core.context_processors.debug',
                               'muddery.web.utils.general_context.general_context',)


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

# Typeclass for NPCs
BASE_NPC_TYPECLASS = "muddery.typeclasses.npcs.MudderyNPC"

# Typeclass for skills
BASE_SKILL_TYPECLASS = "muddery.typeclasses.skills.MudderySkill"

# Typeclass for quests
BASE_QUEST_TYPECLASS = "muddery.typeclasses.quests.MudderyQuest"

######################################################################
# World data features
######################################################################

# attribute's category for data info
WORLD_DATA_INFO_CATEGORY = "data_info"

# data app name
WORLD_DATA_APP = "worlddata"

# data file's folder under user's game directory.
WORLD_DATA_FOLDER = "worlddata/data"

# data file's format, only support csv now.
WORLD_DATA_FILE_TYPE = "csv"

# data file's encoding
WORLD_DATA_FILE_ENCODING = "utf8"

# unique rooms
WORLD_ROOMS = ("world_rooms",)

# unique exits
WORLD_EXITS = ("world_exits",)

# unique objects
WORLD_OBJECTS = ("world_objects",)

# unique npcs
WORLD_NPCS = ("world_npcs",)

# common objects
COMMON_OBJECTS = ("common_objects", "skills", "quests")

# all object data models
OBJECT_DATA_MODELS = (WORLD_ROOMS,
                      WORLD_EXITS,
                      WORLD_OBJECTS,
                      WORLD_NPCS,
                      COMMON_OBJECTS)

# quest data
QUEST_OBJECTIVES = "quest_objectives"
QUEST_DEPENDENCY = "quest_dependency"

# dialogues
DIALOGUES = "dialogues"
DIALOGUE_SENTENCES = "dialogue_sentences"
DIALOGUE_RELATIONS = "dialogue_relations"
NPC_DIALOGUES = "npc_dialogues"
DIALOGUE_QUEST_DEPENDENCY = "dialogue_quest_dependency"

# equip types
EQUIPMENT_TYPES = "equipment_types"

# character levels
CHARACTER_LEVELS = "character_level"

# all other data models
OTHER_DATA_MODELS = (QUEST_OBJECTIVES,
                     QUEST_DEPENDENCY,
                     DIALOGUES,
                     DIALOGUE_SENTENCES,
                     DIALOGUE_RELATIONS,
                     NPC_DIALOGUES,
                     DIALOGUE_QUEST_DEPENDENCY,
                     EQUIPMENT_TYPES,
                     CHARACTER_LEVELS)

# local strings
LOCALIZED_STRINGS_MODEL = "localized_strings"
LOCALIZED_STRINGS_FOLDER = "languages"

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

SKILL_FILES = []
