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
SERVERNAME = "梦幻乐园"

# Path to the game directory (use MUDDERY_DIR to refer to the
# core muddery library)

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

# Server-side websocket port to open for the webclient.
WEBSOCKET_CLIENT_PORT = 8001

# The game server opens an AMP port so that the portal can
# communicate with it.
AMP_PORT = 5000

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
LANGUAGE_CODE = 'zh-cn'


######################################################################
# Django web features
######################################################################

# The secret key is randomly seeded upon creation. It is used to sign
# Django's cookies. Do not share this with anyone. Changing it will
# log out all active web browsing sessions. Game web client sessions
# may survive.
SECRET_KEY = {secret_key}


######################################################################
# World data features
######################################################################

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
                      WORLD_NPCS) + COMMON_OBJECTS

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
                     DEFAULT_OBJECTS,
                     DEFAULT_SKILLS,
                     SHOP_GOODS,
                     NPC_SHOPS,
                     CUSTOM_LOCALIZED_STRINGS,
                     IMAGE_RESOURCES,
                     ICON_RESOURCES,
                     GAME_SETTINGS,
                     CLIENT_SETTINGS) + OBJECT_ADDITIONAL_DATA + EVENT_ADDITIONAL_DATA

EQUIP_EFFECTS = ["attack", "defence"]
