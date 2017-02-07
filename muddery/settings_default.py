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

# Typeclass for NPCs
BASE_NPC_TYPECLASS = "muddery.typeclasses.npcs.MudderyNPC"

# Typeclass for monsters
BASE_MONSTER_TYPECLASS = "muddery.typeclasses.monsters.MudderyMonster"

# Typeclass for skills
BASE_SKILL_TYPECLASS = "muddery.typeclasses.skills.MudderySkill"

# Typeclass for quests
BASE_QUEST_TYPECLASS = "muddery.typeclasses.quests.MudderyQuest"

# Action functions set
ACTION_FUNC_SET = "muddery.statements.default_statement_func_set.ActionFuncSet"

# Condition functions set
CONDITION_FUNC_SET = "muddery.statements.default_statement_func_set.ConditionFuncSet"

# Skill functions set
SKILL_FUNC_SET = "muddery.statements.default_statement_func_set.SkillFuncSet"

# Handler of the combat
COMBAT_HANDLER = "muddery.typeclasses.combat_handler.MudderyCombatHandler"

######################################################################
# World data features
######################################################################

# attribute's category for data info
DATA_KEY_CATEGORY = "data_key"

# data app name
WORLD_DATA_APP = "worlddata"

# data file's folder under user's game directory.
WORLD_DATA_FOLDER = "worlddata/data"

# game settings
GAME_SETTINGS = "game_settings"

# webclient settings
CLIENT_SETTINGS = "client_settings"

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
COMMON_OBJECTS = ("common_objects", "common_characters", "skills", "quests", "equipments", "foods")

# all object data models
OBJECT_DATA_MODELS = (WORLD_ROOMS,
                      WORLD_EXITS,
                      WORLD_OBJECTS,
                      WORLD_NPCS) + COMMON_OBJECTS

# object's additional data
OBJECT_ADDITIONAL_DATA = ("exit_locks", "object_creators")

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

# character skills
DEFAULT_SKILLS = "default_skills"

# resources
IMAGE_RESOURCES = "image_resources"
ICON_RESOURCES = "icon_resources"

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
                     DEFAULT_SKILLS,
                     IMAGE_RESOURCES,
                     ICON_RESOURCES,
                     GAME_SETTINGS,
                     CLIENT_SETTINGS) + OBJECT_ADDITIONAL_DATA + EVENT_ADDITIONAL_DATA

# local strings
LOCALIZED_STRINGS_MODEL = "localized_strings"
LOCALIZED_STRINGS_FOLDER = "languages"

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
