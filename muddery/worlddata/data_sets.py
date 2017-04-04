"""
This module defines available model types.
"""

from muddery.worlddata.data_handler import DataHandler, SystemDataHandler


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
        self.localized_strings = SystemDataHandler("localized_strings")

        self.systemData = [self.class_categories,
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

        self.basicData = [self.equipment_types,
                          self.equipment_positions,
                          self.character_careers,
                          self.career_equipments,
                          self.character_models]

        # Objects data
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

        self.objectData = [self.world_rooms,
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
                           self.shops]

        # Object additional data
        self.objectAdditionalData = [DataHandler("exit_locks"),
                                     DataHandler("two_way_exits"),
                                     DataHandler("object_creators")]

        # Other data
        self.game_settings = DataHandler("game_settings")
        self.client_settings = DataHandler("client_settings")
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
        self.shop_goods = DataHandler("shop_goods")
        self.npc_shops = DataHandler("npc_shops")
        self.image_resources = DataHandler("image_resources")
        self.icon_resources = DataHandler("icon_resources")

        self.otherData = [self.game_settings,
                          self.client_settings,
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
        self.eventAdditionalData = [DataHandler("event_attacks"),
                                    DataHandler("event_dialogues")]

        # all data
        self.allData = []
        self.allData.extend(self.systemData)
        self.allData.extend(self.basicData)
        self.allData.extend(self.objectData)
        self.allData.extend(self.objectAdditionalData)
        self.allData.extend(self.otherData)
        self.allData.extend(self.eventAdditionalData)

        # call creation hook
        self.at_creation()

    def at_creation(self):
        pass


# Data sets
DATA_SETS = DataSets()
