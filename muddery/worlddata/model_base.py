from django.db import models

KEY_LENGTH = 255

#------------------------------------------------------------
#
# store all rooms
#
#------------------------------------------------------------
class world_rooms(models.Model):
    "Store all unique rooms."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=KEY_LENGTH)
    typeclass = models.CharField(max_length=KEY_LENGTH)
    desc = models.TextField(blank=True)

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

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=KEY_LENGTH)
    typeclass = models.CharField(max_length=KEY_LENGTH)
    desc = models.TextField(blank=True)
    verb = models.TextField(blank=True)
    location = models.CharField(max_length=KEY_LENGTH, blank=True)
    destination = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World Exit List"
        verbose_name_plural = "World Exit List"


#------------------------------------------------------------
#
# store exit locks
#
#------------------------------------------------------------
class exit_locks(models.Model):
    "Store all exit locks."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    condition = models.TextField(blank=True)
    verb = models.TextField(blank=True)
    message_lock = models.TextField(blank=True)
    auto_unlock = models.BooleanField(blank=True, default=False)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Exit Lock"
        verbose_name_plural = "Exit Locks"


#------------------------------------------------------------
#
# store all objects
#
#------------------------------------------------------------
class world_objects(models.Model):
    "Store all unique objects."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=KEY_LENGTH)
    typeclass = models.CharField(max_length=KEY_LENGTH)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=KEY_LENGTH, blank=True)
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World Object List"
        verbose_name_plural = "World Object List"


#------------------------------------------------------------
#
# store all object creators
#
#------------------------------------------------------------
class object_creators(world_objects):
    "Store all object creators."

    verb = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Object Creator"
        verbose_name_plural = "Object Creators"


#------------------------------------------------------------
#
# store objects loot list
#
#------------------------------------------------------------
class object_loot_list(models.Model):
    "Store all object creators."

    provider = models.CharField(max_length=KEY_LENGTH, db_index=True)
    object = models.CharField(max_length=KEY_LENGTH)
    number = models.IntegerField(blank=True, default=0)
    odds = models.FloatField(blank=True, default=0)
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Object Creator"
        verbose_name_plural = "Object Creators"
        unique_together = ("provider", "object")


#------------------------------------------------------------
#
# store all common objects
#
#------------------------------------------------------------
class common_objects(models.Model):
    "Store all common objects."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=KEY_LENGTH)
    typeclass = models.CharField(max_length=KEY_LENGTH)
    desc = models.TextField(blank=True)
    max_stack = models.IntegerField(blank=True, default=1)
    unique = models.BooleanField(blank=True, default=False)
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

    type = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=KEY_LENGTH)
    desc = models.TextField(blank=True)
    career = models.CharField(max_length=KEY_LENGTH, blank=True)

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

    position = models.CharField(max_length=KEY_LENGTH, blank=True)
    type = models.CharField(max_length=KEY_LENGTH, blank=True)
    attack = models.IntegerField(blank=True, default=0)
    defence = models.IntegerField(blank=True, default=0)

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

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=KEY_LENGTH)
    typeclass = models.CharField(max_length=KEY_LENGTH)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=KEY_LENGTH, blank=True)
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World NPC List"
        verbose_name_plural = "World NPC List"


#------------------------------------------------------------
#
# store common characters
#
#------------------------------------------------------------
class common_characters(models.Model):
    "Store common characters."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=KEY_LENGTH)
    typeclass = models.CharField(max_length=KEY_LENGTH)
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Common Character List"
        verbose_name_plural = "Common Character List"


#------------------------------------------------------------
#
# store all skills
#
#------------------------------------------------------------
class skills(models.Model):
    "Store all skills."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=KEY_LENGTH)
    typeclass = models.CharField(max_length=KEY_LENGTH)
    desc = models.TextField(blank=True)
    cd = models.IntegerField(blank=True, default=0)
    passive = models.BooleanField(blank=True, default=False)
    condition = models.TextField(blank=True)
    function = models.CharField(max_length=KEY_LENGTH)
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
    
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.TextField(blank=True)
    typeclass = models.CharField(max_length=KEY_LENGTH)
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
    object = models.CharField(max_length=KEY_LENGTH)
    number = models.IntegerField(blank=True, default=0)
    desc = models.TextField(blank=True)

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
# store event data
#
#------------------------------------------------------------
class event_data(models.Model):
    "Store event data."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    object = models.CharField(max_length=KEY_LENGTH, db_index=True)
    type = models.IntegerField()
    trigger = models.IntegerField()
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Event Data"
        verbose_name_plural = "Event Data"


#------------------------------------------------------------
#
# store all dialogues
#
#------------------------------------------------------------
class dialogues(models.Model):
    "Store all dialogues."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
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
    speaker = models.CharField(max_length=KEY_LENGTH, blank=True)
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
    default = models.BooleanField(blank=True, default=False)

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

    character = models.CharField(max_length=KEY_LENGTH, db_index=True)
    level = models.IntegerField()
    max_exp = models.IntegerField()
    max_hp = models.IntegerField()
    max_mp = models.IntegerField()
    attack = models.IntegerField()
    defence = models.IntegerField()

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Character Level List"
        verbose_name_plural = "Character Level List"
        unique_together = ("character", "level")


#------------------------------------------------------------
#
# character skills
#
#------------------------------------------------------------
class character_skill(models.Model):
    "Store all character skill informations."

    character = models.CharField(max_length=KEY_LENGTH, db_index=True)
    skill = models.ForeignKey("skills")

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Character Skill List"
        verbose_name_plural = "Character Skill List"
        unique_together = ("character", "skill")


#------------------------------------------------------------
#
# event mobs
#
#------------------------------------------------------------
class event_mobs(models.Model):
    "Store all event mobs."

    key = models.CharField(max_length=KEY_LENGTH, db_index=True)
    mob = models.CharField(max_length=KEY_LENGTH)
    level = models.IntegerField()
    odds = models.FloatField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Event Mob"
        verbose_name_plural = "Event Mobs"

        
#------------------------------------------------------------
#
# event dialogues
#
#------------------------------------------------------------
class event_dialogues(models.Model):
    "Store all event dialogues."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    dialogue = models.CharField(max_length=KEY_LENGTH)
    npc = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Event Dialogues"
        verbose_name_plural = "Event Dialogues"


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
