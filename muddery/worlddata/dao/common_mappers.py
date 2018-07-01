"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from muddery.worlddata.dao.common_mapper_base import CommonMapper, ObjectsMapper


# ------------------------------------------------------------
#
# objects mapper
#
# ------------------------------------------------------------

WORLD_AREAS = ObjectsMapper("world_areas")

WORLD_EXITS = ObjectsMapper("world_exits")

WORLD_NPCS = ObjectsMapper("world_npcs")

WORLD_OBJECTS = ObjectsMapper("world_objects")

WORLD_ROOMS = ObjectsMapper("world_rooms")

COMMON_OBJECTS = ObjectsMapper("common_objects")

FOODS = ObjectsMapper("foods")

SKILL_BOOKS = ObjectsMapper("skill_books")

EQUIPMENTS = ObjectsMapper("equipments")

COMMON_CHARACTERS = ObjectsMapper("common_characters")

SHOPS = ObjectsMapper("shops")

SHOP_GOODS = ObjectsMapper("shop_goods")

SKILLS = ObjectsMapper("skills")

QUESTS = ObjectsMapper("quests")


# ------------------------------------------------------------
#
# other data mapper
#
# ------------------------------------------------------------

EQUIPMENT_POSITIONS = CommonMapper("equipment_positions")

EQUIPMENT_TYPES = CommonMapper("equipment_types")

EXIT_LOCKS = CommonMapper("exit_locks")

GAME_SETTINGS = CommonMapper("game_settings")

TWO_WAY_EXITS = CommonMapper("two_way_exits")

OBJECT_CREATORS = ObjectsMapper("object_creators")

CREATOR_LOOT_LIST = CommonMapper("creator_loot_list")

CHARACTER_LOOT_LIST = CommonMapper("character_loot_list")

QUEST_REWARD_LIST = CommonMapper("quest_reward_list")

CHARACTER_ATTRIBUTES_INFO = CommonMapper("character_attributes_info")

EQUIPMENT_ATTRIBUTES_INFO = CommonMapper("equipment_attributes_info")

FOOD_ATTRIBUTES_INFO = CommonMapper("food_attributes_info")

CHARACTER_MODELS = CommonMapper("character_models")

DEFAULT_OBJECTS = CommonMapper("default_objects")

NPC_SHOPS = CommonMapper("npc_shops")

SKILL_TYPES = CommonMapper("skill_types")

DEFAULT_SKILLS = CommonMapper("default_skills")

QUEST_OBJECTIVES = CommonMapper("quest_objectives")

QUEST_DEPENDENCIES = CommonMapper("quest_dependencies")

EVENT_DATA = CommonMapper("event_data")

EVENT_ATTACKS = CommonMapper("event_attacks")

EVENT_DIALOGUES = CommonMapper("event_dialogues")

DIALOGUES = CommonMapper("dialogues")

DIALOGUE_QUEST_DEPENDENCIES = CommonMapper("dialogue_quest_dependencies")

DIALOGUE_RELATIONS = CommonMapper("dialogue_relations")

DIALOGUE_SENTENCES = CommonMapper("dialogue_sentences")

NPC_DIALOGUES = CommonMapper("npc_dialogues")

CONDITION_DESC = CommonMapper("condition_desc")

LOCALIZED_STRINGS = CommonMapper("localized_strings")

IMAGE_RESOURCES = CommonMapper("image_resources")
