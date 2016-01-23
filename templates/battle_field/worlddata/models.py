from django.db import models
from muddery.worlddata import model_base


# ------------------------------------------------------------
#
# store all typeclasses
#
# ------------------------------------------------------------
class typeclasses(model_base.typeclasses):
    "store all typeclasses"
    pass


#------------------------------------------------------------
#
# store all rooms
#
#------------------------------------------------------------
class world_rooms(model_base.world_rooms):
    "Store all unique rooms."
    peaceful = models.BooleanField(blank=True, default=False)


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
# store objects loot list
#
#------------------------------------------------------------
class loot_list(model_base.loot_list):
    "Store all object creators."
    pass


#------------------------------------------------------------
#
# store all common objects
#
#------------------------------------------------------------
class common_objects(model_base.common_objects):
    "Store all common objects."
    pass


#------------------------------------------------------------
#
# store all foods
#
#------------------------------------------------------------
class foods(model_base.common_objects):
    "Store all foods."
    hp = models.IntegerField(blank=True, default=0)
    mp = models.IntegerField(blank=True, default=0)


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
# store all equipments
#
#------------------------------------------------------------
class equipments(model_base.equipments):
    "Store all equipments."
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
# store all skills
#
#------------------------------------------------------------
class skills(model_base.skills):
    "Store all skills."
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
# store quest objectives
#
#------------------------------------------------------------
class quest_objectives(model_base.quest_objectives):
    "Store all quest objectives."
    pass


#------------------------------------------------------------
#
# store quest dependency
#
#------------------------------------------------------------
class quest_dependency(model_base.quest_dependency):
    "Store quest dependency."
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


#------------------------------------------------------------
#
# store dialogue quest dependency
#
#------------------------------------------------------------
class dialogue_quest_dependency(model_base.dialogue_quest_dependency):
    "Store dialogue quest dependency."
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
# character skills
#
#------------------------------------------------------------
class character_skills(model_base.character_skills):
    "Store all character skill informations."
    pass


#------------------------------------------------------------
#
# event mobs
#
#------------------------------------------------------------
class event_mobs(model_base.event_mobs):
    "Store all event mobs."
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
# local strings
#
#------------------------------------------------------------
class localized_strings(model_base.localized_strings):
    "Store all server local strings informations."
    pass
