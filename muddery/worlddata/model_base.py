from django.db import models


#------------------------------------------------------------
#
# store all rooms
#
#------------------------------------------------------------
class world_rooms(models.Model):
    "Store all unique rooms."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    attributes = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World Room List"
        verbose_name_plural = "World Room List"


#------------------------------------------------------------
#
# store all exits
#
#------------------------------------------------------------
class world_exits(models.Model):
    "Store all unique exits."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    destination = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World Exit List"
        verbose_name_plural = "World Exit List"


#------------------------------------------------------------
#
# store all objects
#
#------------------------------------------------------------
class world_objects(models.Model):
    "Store all unique objects."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World Object List"
        verbose_name_plural = "World Object List"


#------------------------------------------------------------
#
# store all object creaters
#
#------------------------------------------------------------
class object_creaters(models.Model):
    "Store all object creaters."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)
    obj_list = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Object Creater"
        verbose_name_plural = "Object Creaters"


#------------------------------------------------------------
#
# store all common objects
#
#------------------------------------------------------------
class common_objects(models.Model):
    "Store all common objects."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    max_stack = models.IntegerField(blank=True, default=1)
    unique = models.BooleanField(blank=True, default=False)
    attributes = models.TextField(blank=True)
    effect = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Common Object List"
        verbose_name_plural = "Common Object List"


#------------------------------------------------------------
#
# store all equip_types
#
#------------------------------------------------------------
class equipment_types(models.Model):
    "Store all equip types."

    type = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    career = models.CharField(max_length=255, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Equipment List"
        verbose_name_plural = "Equipment List"


#------------------------------------------------------------
#
# store all equipments
#
#------------------------------------------------------------
class equipments(common_objects):
    "Store all equipments."

    position = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Equipment List"
        verbose_name_plural = "Equipment List"


#------------------------------------------------------------
#
# store all NPCs
#
#------------------------------------------------------------
class world_npcs(models.Model):
    "Store all NPCs."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World NPC List"
        verbose_name_plural = "World NPC List"


#------------------------------------------------------------
#
# store all skills
#
#------------------------------------------------------------
class skills(models.Model):
    "Store all skills."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    cd = models.IntegerField(blank=True, default=0)
    passive = models.BooleanField(blank=True, default=False)
    condition = models.TextField(blank=True)
    function = models.CharField(max_length=255)
    effect = models.FloatField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Skill"
        verbose_name_plural = "Skills"


#------------------------------------------------------------
#
# store all quests
#
#------------------------------------------------------------
class quests(models.Model):
    "Store all quests."
    
    key = models.CharField(max_length=255, primary_key=True)
    name = models.TextField(blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    condition = models.TextField(blank=True)
    action = models.TextField(blank=True)
    
    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest"
        verbose_name_plural = "Quests"


#------------------------------------------------------------
#
# store quest objectives
#
#------------------------------------------------------------
class quest_objectives(models.Model):
    "Store all quest objectives."

    quest = models.ForeignKey("quests", db_index=True)
    ordinal = models.IntegerField()
    type = models.IntegerField()
    object = models.CharField(max_length=255)
    number = models.IntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest Objective"
        verbose_name_plural = "Quest Objectives"
        unique_together = ("quest", "ordinal")


#------------------------------------------------------------
#
# store quest dependency
#
#------------------------------------------------------------
class quest_dependency(models.Model):
    "Store quest dependency."

    quest = models.ForeignKey("quests", db_index=True)
    dependence = models.ForeignKey("quests")
    type = models.IntegerField()

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest Dependency"
        verbose_name_plural = "Quest Dependency"


#------------------------------------------------------------
#
# store all dialogues
#
#------------------------------------------------------------
class dialogues(models.Model):
    "Store all dialogues."

    key = models.CharField(max_length=255, primary_key=True)
    condition = models.TextField(blank=True)
    have_quest = models.ForeignKey("quests", null=True, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Dialogue"
        verbose_name_plural = "Dialogues"


#------------------------------------------------------------
#
# store dialogue relations
#
#------------------------------------------------------------
class dialogue_relations(models.Model):
    "Store dialogue relations."

    dialogue = models.ForeignKey("dialogues", db_index=True)
    next = models.ForeignKey("dialogues")

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Dialogue Relation"
        verbose_name_plural = "Dialogue Relations"


#------------------------------------------------------------
#
# store dialogue sentences
#
#------------------------------------------------------------
class dialogue_sentences(models.Model):
    "Store dialogue sentences."

    dialogue = models.ForeignKey("dialogues", db_index=True)
    ordinal = models.IntegerField()
    speaker = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    action = models.TextField(blank=True)
    provide_quest = models.ForeignKey("quests", null=True, blank=True)
    finish_quest = models.ForeignKey("quests", null=True, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Dialogue Sentence"
        verbose_name_plural = "Dialogue Sentences"


#------------------------------------------------------------
#
# store npc's dialogue
#
#------------------------------------------------------------
class npc_dialogues(models.Model):
    "Store npc's dialogues."

    npc = models.ForeignKey("world_npcs", db_index=True)
    dialogue = models.ForeignKey("dialogues", db_index=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "NPC Dialogue"
        verbose_name_plural = "NPC Dialogues"


#------------------------------------------------------------
#
# store dialogue quest dependency
#
#------------------------------------------------------------
class dialogue_quest_dependency(models.Model):
    "Store dialogue quest dependency."

    dialogue = models.ForeignKey("dialogues", db_index=True)
    dependence = models.ForeignKey("quests")
    type = models.IntegerField()

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Dialogue Quest Dependency"
        verbose_name_plural = "Dialogue Quest Dependency"


#------------------------------------------------------------
#
# character levels
#
#------------------------------------------------------------
class character_level(models.Model):
    "Store all character level informations."

    level = models.IntegerField(primary_key=True)
    max_exp = models.IntegerField()

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Character Level List"
        verbose_name_plural = "Character Level List"


#------------------------------------------------------------
#
# local strings
#
#------------------------------------------------------------
class localized_strings(models.Model):
    "Store all server local strings informations."

    origin = models.TextField(primary_key=True)
    local = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Server Local String"
        verbose_name_plural = "Server Local Strings"
