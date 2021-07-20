"""
This model translates default strings into localized strings.
"""

from muddery.worldeditor.dao.common_mapper_base import CommonMapper, ObjectsMapper


# ------------------------------------------------------------
#
# objects mapper
#
# ------------------------------------------------------------

WORLD_AREAS = ObjectsMapper("AREA")

WORLD_EXITS = ObjectsMapper("EXIT")

WORLD_NPCS = ObjectsMapper("WORLD_NPC")

WORLD_OBJECTS = ObjectsMapper("WORLD_OBJECT")

OBJECT_CREATORS = ObjectsMapper("WORLD_OBJECT_CREATOR")

WORLD_ROOMS = ObjectsMapper("ROOM")

COMMON_OBJECTS = ObjectsMapper("COMMON_OBJECT")

POCKET_OBJECTS = ObjectsMapper("POCKET_OBJECT")

FOODS = ObjectsMapper("FOOD")

SKILL_BOOKS = ObjectsMapper("SKILL_BOOK")

EQUIPMENTS = ObjectsMapper("EQUIPMENT")

CHARACTERS = ObjectsMapper("CHARACTER")

PLAYER_CHARACTERS = ObjectsMapper("PLAYER_CHARACTER")

SHOPS = ObjectsMapper("SHOP")

SHOP_GOODS = ObjectsMapper("SHOP_GOODS")

SKILLS = ObjectsMapper("SKILL")

QUESTS = ObjectsMapper("QUEST")


# ------------------------------------------------------------
#
# other data mapper
#
# ------------------------------------------------------------

EQUIPMENT_POSITIONS = CommonMapper("equipment_positions")

EQUIPMENT_TYPES = CommonMapper("equipment_types")

GAME_SETTINGS = CommonMapper("game_settings")

HONOUR_SETTINGS = CommonMapper("honour_settings")

CREATOR_LOOT_LIST = CommonMapper("creator_loot_list")

CHARACTER_LOOT_LIST = CommonMapper("character_loot_list")

QUEST_REWARD_LIST = CommonMapper("quest_reward_list")

PROPERTIES_DICT = CommonMapper("properties_dict")

DEFAULT_OBJECTS = CommonMapper("default_objects")

NPC_SHOPS = CommonMapper("npc_shops")

SKILL_TYPES = CommonMapper("skill_types")

DEFAULT_SKILLS = CommonMapper("default_skills")

QUEST_OBJECTIVES = CommonMapper("quest_objectives")

QUEST_DEPENDENCIES = CommonMapper("quest_dependencies")

EVENT_DATA = CommonMapper("event_data")

ACTION_ATTACK = CommonMapper("action_attack")

ACTION_DIALOGUE = CommonMapper("action_dialogue")

ACTION_LEARN_SKILL = CommonMapper("action_learn_skill")

ACTION_ACCEPT_QUEST = CommonMapper("action_accept_quest")

ACTION_TURN_IN_QUEST = CommonMapper("action_turn_in_quest")

ACTION_CLOSE_EVENT = CommonMapper("action_close_event")

DIALOGUES = CommonMapper("dialogues")

DIALOGUE_QUEST_DEPENDENCIES = CommonMapper("dialogue_quest_dependencies")

DIALOGUE_RELATIONS = CommonMapper("dialogue_relations")

NPC_DIALOGUES = CommonMapper("npc_dialogues")

LOCALIZED_STRINGS = CommonMapper("localized_strings")

IMAGE_RESOURCES = CommonMapper("image_resources")
