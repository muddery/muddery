"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from muddery.worlddata.dao.model_mapper_base import BaseCommonMapper, BaseObjectsMapper


# ------------------------------------------------------------
#
# objects mapper
#
# ------------------------------------------------------------

WORLD_AREAS = BaseObjectsMapper("world_areas")

WORLD_EXITS = BaseObjectsMapper("world_exits")

WORLD_NPCS = BaseObjectsMapper("world_npcs")

WORLD_OBJECTS = BaseObjectsMapper("world_objects")

WORLD_ROOMS = BaseObjectsMapper("world_rooms")

COMMON_OBJECTS = BaseObjectsMapper("common_objects")

FOODS = BaseObjectsMapper("foods")

SKILL_BOOKS = BaseObjectsMapper("skill_books")

EQUIPMENTS = BaseObjectsMapper("equipments")

COMMON_CHARACTERS = BaseObjectsMapper("common_characters")

# ------------------------------------------------------------
#
# other data mapper
#
# ------------------------------------------------------------

EQUIPMENT_POSITIONS = BaseCommonMapper("equipment_positions")

EQUIPMENT_TYPES = BaseCommonMapper("equipment_types")

EXIT_LOCKS = BaseCommonMapper("exit_locks")

GAME_SETTINGS = BaseCommonMapper("game_settings")

TWO_WAY_EXITS = BaseCommonMapper("two_way_exits")

OBJECT_CREATORS = BaseObjectsMapper("object_creators")

CREATOR_LOOT_LIST = BaseCommonMapper("creator_loot_list")

LOOT_LIST = BaseCommonMapper("loot_list")

CHARACTER_LOOT_LIST = BaseCommonMapper("character_loot_list")

QUEST_REWARD_LIST = BaseCommonMapper("quest_reward_list")

CHARACTER_ATTRIBUTES_INFO = BaseCommonMapper("character_attributes_info")

EQUIPMENT_ATTRIBUTES_INFO = BaseCommonMapper("equipment_attributes_info")

FOOD_ATTRIBUTES_INFO = BaseCommonMapper("food_attributes_info")

CHARACTER_MODELS = BaseCommonMapper("character_models")

DEFAULT_OBJECTS = BaseCommonMapper("default_objects")

NPC_SHOPS = BaseCommonMapper("npc_shops")

SKILL_TYPES = BaseCommonMapper("skill_types")

DEFAULT_SKILLS = BaseCommonMapper("default_skills")

QUEST_OBJECTIVES = BaseCommonMapper("quest_objectives")

QUEST_DEPENDENCIES = BaseCommonMapper("quest_dependencies")

EVENT_DATA = BaseCommonMapper("event_data")

DIALOGUES = BaseCommonMapper("dialogues")

DIALOGUE_QUEST_DEPENDENCIES = BaseCommonMapper("dialogue_quest_dependencies")

DIALOGUE_RELATIONS = BaseCommonMapper("dialogue_relations")

DIALOGUE_SENTENCES = BaseCommonMapper("dialogue_sentences")

NPC_DIALOGUES = BaseCommonMapper("npc_dialogues")

EVENT_ATTACKS = BaseCommonMapper("event_attacks")

EVENT_DIALOGUES = BaseCommonMapper("event_dialogues")

CONDITION_DESC = BaseCommonMapper("condition_desc")

LOCALIZED_STRINGS = BaseCommonMapper("localized_strings")

IMAGE_RESOURCES = BaseCommonMapper("image_resources")

ICON_RESOURCES = BaseCommonMapper("icon_resources")
