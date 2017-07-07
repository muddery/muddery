"""
This module defines available model types.
"""

from django.conf import settings
from evennia.utils.utils import class_from_module
from muddery.worlddata.data_handler import DataHandler, SystemDataHandler, LocalizedStringsHandler


class DataSets(object):

    def __init__(self):
        """
        Load data settings.

        Returns:
            None.
        """
        # System settings
        self.class_categories = SystemDataHandler("class_categories")
        self.typeclasses = SystemDataHandler("typeclasses")
        self.event_types = SystemDataHandler("event_types")
        self.event_trigger_types = SystemDataHandler("event_trigger_types")
        self.quest_objective_types = SystemDataHandler("quest_objective_types")
        self.quest_dependency_types = SystemDataHandler("quest_dependency_types")
        self.localized_strings = LocalizedStringsHandler("localized_strings")

        self.system_data = [self.class_categories,
                            self.typeclasses,
                            self.event_types,
                            self.event_trigger_types,
                            self.quest_objective_types,
                            self.quest_dependency_types,
                            self.localized_strings]

        # Basic settings
        self.equipment_types = DataHandler("equipment_types")
        self.equipment_positions = DataHandler("equipment_positions")
        self.character_careers = DataHandler("character_careers")
        self.career_equipments = DataHandler("career_equipments")
        self.character_models = DataHandler("character_models")

        self.basic_data = [self.equipment_types,
                           self.equipment_positions,
                           self.character_careers,
                           self.career_equipments,
                           self.character_models]

        # Objects data
        self.world_areas = DataHandler("world_areas")
        self.world_rooms = DataHandler("world_rooms")
        self.world_exits = DataHandler("world_exits")
        self.world_objects = DataHandler("world_objects")
        self.world_npcs = DataHandler("world_npcs")
        self.common_objects = DataHandler("common_objects")
        self.common_characters = DataHandler("common_characters")
        self.skills = DataHandler("skills")
        self.quests = DataHandler("quests")
        self.equipments = DataHandler("equipments")
        self.foods = DataHandler("foods")
        self.skill_books = DataHandler("skill_books")
        self.shops = DataHandler("shops")
        self.shop_goods = DataHandler("shop_goods")

        self.object_data = [self.world_areas,
                            self.world_rooms,
                            self.world_exits,
                            self.world_objects,
                            self.world_npcs,
                            self.common_objects,
                            self.common_characters,
                            self.skills,
                            self.quests,
                            self.equipments,
                            self.foods,
                            self.skill_books,
                            self.shops,
                            self.shop_goods]

        # Object additional data
        self.exit_locks = DataHandler("exit_locks")
        self.two_way_exits = DataHandler("two_way_exits")
        self.object_creators = DataHandler("object_creators")
        
        self.object_additional_data = [self.exit_locks,
                                       self.two_way_exits,
                                       self.object_creators]

        # Other data
        self.game_settings = DataHandler("game_settings")
        self.character_attributes_info = DataHandler("character_attributes_info")
        self.equipment_attributes_info = DataHandler("equipment_attributes_info")
        self.food_attributes_info = DataHandler("food_attributes_info")
        self.creator_loot_list = DataHandler("creator_loot_list")
        self.character_loot_list = DataHandler("character_loot_list")
        self.quest_reward_list = DataHandler("quest_reward_list")
        self.quest_objectives = DataHandler("quest_objectives")
        self.quest_dependencies = DataHandler("quest_dependencies")
        self.event_data = DataHandler("event_data")
        self.dialogues = DataHandler("dialogues")
        self.dialogue_sentences = DataHandler("dialogue_sentences")
        self.dialogue_relations = DataHandler("dialogue_relations")
        self.npc_dialogues = DataHandler("npc_dialogues")
        self.dialogue_quest_dependencies = DataHandler("dialogue_quest_dependencies")
        self.default_objects = DataHandler("default_objects")
        self.default_skills = DataHandler("default_skills")
        self.npc_shops = DataHandler("npc_shops")
        self.image_resources = DataHandler("image_resources")
        self.icon_resources = DataHandler("icon_resources")

        self.other_data = [self.game_settings,
                           self.character_attributes_info,
                           self.equipment_attributes_info,
                           self.food_attributes_info,
                           self.creator_loot_list,
                           self.character_loot_list,
                           self.quest_reward_list,
                           self.quest_objectives,
                           self.quest_dependencies,
                           self.event_data,
                           self.dialogues,
                           self.dialogue_sentences,
                           self.dialogue_relations,
                           self.npc_dialogues,
                           self.dialogue_quest_dependencies,
                           self.default_objects,
                           self.default_skills,
                           self.shop_goods,
                           self.npc_shops,
                           self.image_resources,
                           self.icon_resources]

        # Event additional data
        self.event_attacks = DataHandler("event_attacks")
        self.event_dialogues = DataHandler("event_dialogues")

        self.event_additional_data = [self.event_attacks,
                                      self.event_dialogues]

        # all data handlers
        self.all_handlers = []
        
        # data handler dict
        self.handler_dict = {}

        # update data dict after hook
        self.update_data_sets()
        
        # call creation hook
        self.at_creation()

    def update_data_sets(self):
        # all data handlers
        self.all_handlers = []
        self.all_handlers.extend(self.system_data)
        self.all_handlers.extend(self.basic_data)
        self.all_handlers.extend(self.object_data)
        self.all_handlers.extend(self.object_additional_data)
        self.all_handlers.extend(self.other_data)
        self.all_handlers.extend(self.event_additional_data)
        
        # data handler dict
        self.handler_dict = {}
        for data_handler in self.all_handlers:
            self.handler_dict[data_handler.model_name] = data_handler

    def add_data_handler(self, group, data_handler):
        if group:
            group.append(data_handler)
        
        self.all_handlers.append(data_handler)
        self.handler_dict[data_handler.model_name] = data_handler

    def get_handler(self, model_name):
        """
        Get a data handler by model name.
        """
        return self.handler_dict.get(model_name, None)

    def at_creation(self):
        pass


# Data sets
DATA_SETS = class_from_module(settings.DATA_SETS)()
