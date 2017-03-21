"""
This module defines available model types.
"""


class BasicData(object):
    pass


class ObjectsData(object):

    # unique rooms
    WORLD_ROOMS = "world_rooms"

    # unique exits
    WORLD_EXITS = "world_exits"

    # unique objects
    WORLD_OBJECTS = "world_objects"

    # unique npcs
    WORLD_NPCS = "world_npcs"

    # common objects
    COMMON_OBJECTS = "common_objects"

    # common characters
    COMMON_CHARACTERS = "common_characters"

    # skills
    SKILLS = "skills"

    # quests
    QUESTS = "quests"

    #equipments
    EQUIPMENTS = "equipments"

    # foods
    FOODS = "foods"

    # skill books
    SKILL_BOOKS = "skill_books"

    # shops
    SHOPS = "shops"


class ObjectsAdditionalData(object):

    # exit locks
    EXIT_LOCKS = "exit_locks"

    # two way exits
    TWO_WAY_EXITS = "two_way_exits"

    # object creators
    OBJECT_CREATORS = "object_creators"


class OtherData(object):

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

    # localized string
    LOCALIZED_STRINGS = "localized_strings"


class EventAdditionalData(object):
    """
    Event additional data. One event can have one additional data model.
    """

    EVENT_ATTACKS = "event_attacks"
    EVENT_DIALOGUES = "event_dialogues"


class OtherSettings(object):

    # game settings
    GAME_SETTINGS = "game_settings"

    # webclient settings
    CLIENT_SETTINGS = "client_settings"

    SYSTEM_LOCALIZED_STRINGS_FOLDER = "languages"
