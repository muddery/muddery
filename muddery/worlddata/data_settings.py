"""
This module defines available model types.
"""


class DataSettingsBase(object):
    """
    Base methods of data setting classes.
    """
    def __init__(self):
        """
        Set data.

        Returns:
            None.
        """
        self._all_data = []

    def all(self):
        """
        Get all models.

        Returns:
            list: all data model's name.
        """
        if not self._all_data:
            names = [name for name in dir(self.__class__) if name[0] != "_" and name.isupper()]
            self._all_data = [getattr(self, name) for name in names]
        return self._all_data


class SystemData(DataSettingsBase):

    # class's categories
    CLASS_CATEGORIES = "class_categories"

    # typeclasses
    TYPECLASSES = "typeclasses"

    # event types
    EVENT_TYPES = "event_types"

    # event trigger types
    EVENT_TRIGGER_TYPES = "event_trigger_types"

    # quest objective types
    QUEST_OBJECTIVE_TYPES = "quest_objective_types"

    # quest dependency types
    QUEST_DEPENDENCY_TYPES = "quest_dependency_types"


class BasicData(DataSettingsBase):

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


class ObjectsData(DataSettingsBase):

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


class ObjectsAdditionalData(DataSettingsBase):

    # exit locks
    EXIT_LOCKS = "exit_locks"

    # two way exits
    TWO_WAY_EXITS = "two_way_exits"

    # object creators
    OBJECT_CREATORS = "object_creators"


class OtherData(DataSettingsBase):

    # game settings
    GAME_SETTINGS = "game_settings"

    # webclient settings
    CLIENT_SETTINGS = "client_settings"

    # loot lists
    CREATOR_LOOT_LIST = "creator_loot_list"
    CHARACTER_LOOT_LIST = "character_loot_list"
    QUEST_REWARD_LIST = "quest_reward_list"

    # quest data
    QUEST_OBJECTIVES = "quest_objectives"
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


class EventAdditionalData(DataSettingsBase):
    """
    Event additional data. One event can have one additional data model.
    """

    EVENT_ATTACKS = "event_attacks"
    EVENT_DIALOGUES = "event_dialogues"
