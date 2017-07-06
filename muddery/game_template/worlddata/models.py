from django.db import models
from muddery.worlddata import model_base


# ------------------------------------------------------------
#
# game's basic settings
#
# ------------------------------------------------------------
class game_settings(model_base.game_settings):
    """
    Game's basic settings.
    """
    pass


# ------------------------------------------------------------
#
# all class's categories
#
# ------------------------------------------------------------
class class_categories(model_base.class_categories):
    "all class's categories"
    pass


# ------------------------------------------------------------
#
# store all typeclasses
#
# ------------------------------------------------------------
class typeclasses(model_base.typeclasses):
    "store all typeclasses"
    pass


# ------------------------------------------------------------
#
# world areas
#
# ------------------------------------------------------------
class world_areas(model_base.world_areas):
    "Rooms belongs to areas."
    pass
    

#------------------------------------------------------------
#
# store all rooms
#
#------------------------------------------------------------
class world_rooms(model_base.world_rooms):
    "Store all unique rooms."
    pass


#------------------------------------------------------------
#
# store all exits
#
#------------------------------------------------------------
class world_exits(model_base.world_exits):
    "Store all unique exits."
    pass


#------------------------------------------------------------
#
# store exit locks
#
#------------------------------------------------------------
class exit_locks(model_base.exit_locks):
    "Store all exit locks."
    pass


#------------------------------------------------------------
#
# two way exit's additional data
#
#------------------------------------------------------------
class two_way_exits(model_base.two_way_exits):
    "Store all exit locks."
    pass


#------------------------------------------------------------
#
# store all objects
#
#------------------------------------------------------------
class world_objects(model_base.world_objects):
    "Store all unique objects."
    pass


#------------------------------------------------------------
#
# store all object creators
#
#------------------------------------------------------------
class object_creators(model_base.object_creators):
    "Store all object creators."
    pass


#------------------------------------------------------------
#
# object creator's loot list
#
#------------------------------------------------------------
class creator_loot_list(model_base.creator_loot_list):
    "Object creator's loot list"
    pass


#------------------------------------------------------------
#
# store all common objects
#
#------------------------------------------------------------
class common_objects(model_base.common_objects):
    "Store all common objects."
    pass


# ------------------------------------------------------------
#
# store all foods
#
# ------------------------------------------------------------
class foods(model_base.foods):
    "Foods inherit from common objects."
    pass


# ------------------------------------------------------------
#
# store all skill books
#
# ------------------------------------------------------------
class skill_books(model_base.skill_books):
    "Skill books inherit from common objects."
    pass
    

#------------------------------------------------------------
#
# store all equip_types
#
#------------------------------------------------------------
class equipment_types(model_base.equipment_types):
    "Store all equip types."
    pass


#------------------------------------------------------------
#
# store all equip_positions
#
#------------------------------------------------------------
class equipment_positions(model_base.equipment_positions):
    "Store all equip types."
    pass


#------------------------------------------------------------
#
# store all equipments
#
#------------------------------------------------------------
class equipments(model_base.equipments):
    "Store all equipments."


# ------------------------------------------------------------
#
# store all careers
#
# ------------------------------------------------------------
class character_careers(model_base.character_careers):
    "Store all careers."
    pass


# ------------------------------------------------------------
#
# store career and equipment type's relationship
#
# ------------------------------------------------------------
class career_equipments(model_base.career_equipments):
    "Store career and equipment type's relationship."
    pass



# ------------------------------------------------------------
#
# character attributes
#
# ------------------------------------------------------------
class character_attributes_info(model_base.character_attributes_info):
    "character attributes"
    pass


# ------------------------------------------------------------
#
# Equipment attribute's information.
#
# ------------------------------------------------------------
class equipment_attributes_info(model_base.equipment_attributes_info):
    "Equipment's all available attributes"
    pass


# ------------------------------------------------------------
#
# Food attribute's information.
#
# ------------------------------------------------------------
class food_attributes_info(model_base.food_attributes_info):
    "Food attribute's information."
    pass


#------------------------------------------------------------
#
# character levels
#
#------------------------------------------------------------
class character_models(model_base.character_models):
    "Store all character level informations."
    pass


#------------------------------------------------------------
#
# store all npcs
#
#------------------------------------------------------------
class world_npcs(model_base.world_npcs):
    "Store all unique objects."
    pass


#------------------------------------------------------------
#
# store common characters
#
#------------------------------------------------------------
class common_characters(model_base.common_characters):
    "Store all common characters."
    pass


#------------------------------------------------------------
#
# character's loot list
#
#------------------------------------------------------------
class character_loot_list(model_base.character_loot_list):
    "Character's loot list"
    pass


#------------------------------------------------------------
#
# character's default objects
#
#------------------------------------------------------------
class default_objects(model_base.default_objects):
    "Store character's default objects information."
    pass
    

# ------------------------------------------------------------
#
# shops
#
# ------------------------------------------------------------
class shops(model_base.shops):
    "Store all shops."
    pass
        
        
# ------------------------------------------------------------
#
# shop goods
#
# ------------------------------------------------------------
class shop_goods(model_base.shop_goods):
    "All goods that sold in shops."
    pass


# ------------------------------------------------------------
#
# npc shops
#
# ------------------------------------------------------------
class npc_shops(model_base.npc_shops):
    "Store npc's shops."
    pass
    
    
#------------------------------------------------------------
#
# store all skills
#
#------------------------------------------------------------
class skills(model_base.skills):
    "Store all skills."
    pass


#------------------------------------------------------------
#
# character skills
#
#------------------------------------------------------------
class default_skills(model_base.default_skills):
    "Store all character skill informations."
    pass


#------------------------------------------------------------
#
# store all quests
#
#------------------------------------------------------------
class quests(model_base.quests):
    "Store all dramas."
    pass


#------------------------------------------------------------
#
# quest's reward list
#
#------------------------------------------------------------
class quest_reward_list(model_base.quest_reward_list):
    "Quest's reward list"
    pass


# ------------------------------------------------------------
#
# quest objective's type
#
# ------------------------------------------------------------
class quest_objective_types(model_base.quest_objective_types):
    "quest objective's type"
    pass


#------------------------------------------------------------
#
# store quest objectives
#
#------------------------------------------------------------
class quest_objectives(model_base.quest_objectives):
    "Store all quest objectives."
    pass


#------------------------------------------------------------
#
# store quest dependency types
#
#------------------------------------------------------------
class quest_dependency_types(model_base.quest_dependency_types):
    "Store quest dependency."
    pass


#------------------------------------------------------------
#
# store quest dependencies
#
#------------------------------------------------------------
class quest_dependencies(model_base.quest_dependencies):
    "Store quest dependency."
    pass


# ------------------------------------------------------------
#
# event's type
#
# ------------------------------------------------------------
class event_types(model_base.event_types):
    "Event's type"
    pass


# ------------------------------------------------------------
#
# event triggers
#
# ------------------------------------------------------------
class event_trigger_types(model_base.event_trigger_types):
    "Event's trigger types"
    pass


#------------------------------------------------------------
#
# store event data
#
#------------------------------------------------------------
class event_data(model_base.event_data):
    "Store event data."
    pass


#------------------------------------------------------------
#
# store all dialogues
#
#------------------------------------------------------------
class dialogues(model_base.dialogues):
    "Store all dialogues."
    pass


#------------------------------------------------------------
#
# store dialogue quest dependencies
#
#------------------------------------------------------------
class dialogue_quest_dependencies(model_base.dialogue_quest_dependencies):
    "Store dialogue quest dependencies."
    pass


#------------------------------------------------------------
#
# store dialogue relations
#
#------------------------------------------------------------
class dialogue_relations(model_base.dialogue_relations):
    "Store dialogue relations."
    pass


#------------------------------------------------------------
#
# store dialogue sentences
#
#------------------------------------------------------------
class dialogue_sentences(model_base.dialogue_sentences):
    "Store dialogue sentences."
    pass


#------------------------------------------------------------
#
# store npc's dialogue
#
#------------------------------------------------------------
class npc_dialogues(model_base.npc_dialogues):
    "Store all dialogues."
    pass


# ------------------------------------------------------------
#
# event attack's data
#
# ------------------------------------------------------------
class event_attacks(model_base.event_attacks):
    "event attack's data"
    pass


#------------------------------------------------------------
#
# event dialogues
#
#------------------------------------------------------------
class event_dialogues(model_base.event_dialogues):
    "Store all event dialogues."
    pass


#------------------------------------------------------------
#
# localized strings
#
#------------------------------------------------------------
class localized_strings(model_base.localized_strings):
    "Store all system localized strings."
    pass


#------------------------------------------------------------
#
# image resources
#
#------------------------------------------------------------
class image_resources(model_base.image_resources):
    "Store all image resource's information."
    pass


#------------------------------------------------------------
#
# icon resources
#
#------------------------------------------------------------
class icon_resources(model_base.icon_resources):
    "Store all icon resource's information."
    pass
