from django.db import models
from muddery.worlddata import model_base


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
# store all objects
#
#------------------------------------------------------------
class world_objects(model_base.world_objects):
    "Store all unique objects."
    pass


#------------------------------------------------------------
#
# store all object creaters
#
#------------------------------------------------------------
class object_creaters(model_base.object_creaters):
    "Store all object creaters."
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
    attack = models.IntegerField(blank=True, default=0)
    defence = models.IntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        verbose_name = "Equipment List"
        verbose_name_plural = "Equipment List"


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
# character levels
#
#------------------------------------------------------------
class character_level(model_base.character_level):
    "Store all character level informations."
    max_hp = models.IntegerField()
    max_mp = models.IntegerField()
    attack = models.IntegerField()
    defence = models.IntegerField()


#------------------------------------------------------------
#
# local strings
#
#------------------------------------------------------------
class localized_strings(model_base.localized_strings):
    "Store all server local strings informations."
    pass
