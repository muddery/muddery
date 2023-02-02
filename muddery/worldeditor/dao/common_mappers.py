"""
This model translates default strings into localized strings.
"""

from muddery.worldeditor.dao.common_mapper_base import CommonMapper, ElementsMapper


# ------------------------------------------------------------
#
# objects mapper
#
# ------------------------------------------------------------

WORLD_AREAS = ElementsMapper("AREA")

WORLD_EXITS = ElementsMapper("EXIT")

WORLD_NPCS = ElementsMapper("WORLD_NPC")

WORLD_OBJECTS = ElementsMapper("WORLD_OBJECT")

OBJECT_CREATORS = ElementsMapper("WORLD_OBJECT_CREATOR")

WORLD_ROOMS = ElementsMapper("ROOM")

COMMON_OBJECTS = ElementsMapper("COMMON_OBJECT")

POCKET_OBJECTS = ElementsMapper("POCKET_OBJECT")

FOODS = ElementsMapper("FOOD")

SKILL_BOOKS = ElementsMapper("SKILL_BOOK")

EQUIPMENTS = ElementsMapper("EQUIPMENT")

CHARACTERS = ElementsMapper("CHARACTER")

PLAYER_CHARACTERS = ElementsMapper("PLAYER_CHARACTER")

SHOPS = ElementsMapper("SHOP")

SHOP_GOODS = ElementsMapper("SHOP_GOODS")

SKILLS = ElementsMapper("SKILL")

QUESTS = ElementsMapper("QUEST")


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

QUEST_RELATIONS = CommonMapper("quest_relations")

EVENT_DATA = CommonMapper("event_data")

ACTION_ATTACK = CommonMapper("action_attack")

ACTION_DIALOGUE = CommonMapper("action_dialogue")

ACTION_LEARN_SKILL = CommonMapper("action_learn_skill")

ACTION_ACCEPT_QUEST = CommonMapper("action_accept_quest")

ACTION_TURN_IN_QUEST = CommonMapper("action_turn_in_quest")

ACTION_CLOSE_EVENT = CommonMapper("action_close_event")

DIALOGUES = CommonMapper("dialogues")

DIALOGUE_RELATIONS = CommonMapper("dialogue_relations")

NPC_DIALOGUES = CommonMapper("npc_dialogues")

LOCALIZED_STRINGS = CommonMapper("localized_strings")
