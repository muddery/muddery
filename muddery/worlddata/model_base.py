from django.db import models

KEY_LENGTH = 255
NAME_LENGTH = 20
TYPECLASS_LENGTH = 80
POSITION_LENGTH = 80


# ------------------------------------------------------------
#
# store all typeclasses
#
# ------------------------------------------------------------
class typeclasses(models.Model):
    "store all typeclasses"

    # typeclass's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # the readable name of the typeclass
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    # the typeclass's path that related to a class
    path = models.CharField(max_length=TYPECLASS_LENGTH, blank=True)

    # typeclass's description (optional)
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Typeclass"
        verbose_name_plural = "Typeclasses"

    def __unicode__(self):
        return self.name


# ------------------------------------------------------------
#
# store all rooms
#
# ------------------------------------------------------------
class world_rooms(models.Model):
    "Store all unique rooms."

    # room's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # room's name for display
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # room's typeclass
    typeclass = models.ForeignKey("typeclasses")

    # room's description for display
    desc = models.TextField(blank=True)

    # room's position which is used in map
    position = models.CharField(max_length=POSITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __unicode__(self):
        return self.key


# ------------------------------------------------------------
#
# store all exits
#
# ------------------------------------------------------------
class world_exits(models.Model):
    "Store all unique exits."

    # exit's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # exit's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # exit's typeclass
    typeclass = models.ForeignKey("typeclasses")

    # exit's description for display
    desc = models.TextField(blank=True)

    # the action verb to enter the exit (optional)
    verb = models.CharField(max_length=NAME_LENGTH, blank=True)

    # the exit's location, it must be a room
    location = models.ForeignKey("world_rooms")

    # the exits's destination
    destination = models.ForeignKey("world_rooms")

    # the condition for showing the exit
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Exit"
        verbose_name_plural = "Exits"

    def __unicode__(self):
        return self.key


# ------------------------------------------------------------
#
# locked exit's additional data
#
# ------------------------------------------------------------
class exit_locks(models.Model):
    "locked exit's additional data"

    # related exit
    key = models.OneToOneField("world_exits")

    # condition of the lock
    unlock_condition = models.TextField(blank=True)

    # action to unlock the exit (optional)
    unlock_verb = models.CharField(max_length=NAME_LENGTH, blank=True)

    # description when locked
    locked_desc = models.TextField(blank=True)

    # if the exit can be unlocked automatically
    auto_unlock = models.BooleanField(blank=True, default=False)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Exit Lock"
        verbose_name_plural = "Exit Locks"


# ------------------------------------------------------------
#
# store all objects
#
# ------------------------------------------------------------
class world_objects(models.Model):
    "Store all unique objects."

    # object's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # object's name
    name = models.CharField(max_length=NAME_LENGTH)

    # object's typeclass
    typeclass = models.ForeignKey("typeclasses")

    # the object's destination
    desc = models.TextField(blank=True)

    # object's location, it must be a room
    location = models.ForeignKey("world_rooms")

    # the condition for showing the object
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World Object"
        verbose_name_plural = "World Objects"

    def __unicode__(self):
        return self.key


# ------------------------------------------------------------
#
# object creator's additional data
#
# ------------------------------------------------------------
class object_creators(models.Model):
    "object creator's additional data"

    # related object
    key = models.OneToOneField("world_objects")

    # loot's verb
    loot_verb = models.CharField(max_length=NAME_LENGTH, blank=True)

    # loot's condition
    loot_condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Object Creator"
        verbose_name_plural = "Object Creators"


# ------------------------------------------------------------
#
# store objects loot list
#
# ------------------------------------------------------------
class loot_list(models.Model):
    "Store all object creators."

    # the provider of the object
    provider = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # the key of dropped object
    object = models.CharField(max_length=KEY_LENGTH)

    # number of dropped object
    number = models.IntegerField(blank=True, default=0)

    # odds of drop, from 0.0 to 1.0
    odds = models.FloatField(blank=True, default=0)

    # the player must have this quest, or will not drop
    quest = models.CharField(max_length=KEY_LENGTH)

    # condition of the drop
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Loot List"
        verbose_name_plural = "Loot Lists"
        unique_together = ("provider", "object")


# ------------------------------------------------------------
#
# store all common objects
#
# ------------------------------------------------------------
class common_objects(models.Model):
    "Store all common objects."

    # object's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # object's name
    name = models.CharField(max_length=NAME_LENGTH)

    # object's typeclass
    typeclass = models.ForeignKey("typeclasses")

    # object's description
    desc = models.TextField(blank=True)

    # the max number of this object in one pile, must above 1
    max_stack = models.IntegerField(blank=True, default=1)

    # if can have only one pile of this object
    unique = models.BooleanField(blank=True, default=False)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Common Object"
        verbose_name_plural = "Common Objects"


# ------------------------------------------------------------
#
# store all equip_types
#
# ------------------------------------------------------------
class equipment_types(models.Model):
    "Store all equip types."

    # equipment type's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # type's name
    name = models.CharField(max_length=NAME_LENGTH)

    # type's description
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Equipment's Type"
        verbose_name_plural = "Equipment's Types"

    def __unicode__(self):
        return self.name


# ------------------------------------------------------------
#
# store all available equipment potisions
#
# ------------------------------------------------------------
class equipment_positions(models.Model):
    "Store all equip types."

    # position's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # position's name
    name = models.CharField(max_length=NAME_LENGTH)

    # position's description
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Equipment's Position"
        verbose_name_plural = "Equipment's Positions"

    def __unicode__(self):
        return self.name

# ------------------------------------------------------------
#
# store all equipments
#
# ------------------------------------------------------------
class equipments(common_objects):
    "Store all equipments."

    # equipment's position
    position = models.ForeignKey("equipment_positions")

    # equipment's type
    type = models.ForeignKey("equipment_types")

    # attack effect
    attack = models.IntegerField(blank=True, default=0)

    # defence effect
    defence = models.IntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Equipment"
        verbose_name_plural = "Equipments"


# ------------------------------------------------------------
#
# store all careers
#
# ------------------------------------------------------------
class character_careers(models.Model):
    "Store all careers."

    # careers's type
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # careers's name
    name = models.CharField(max_length=NAME_LENGTH)

    # careers's description
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Career"
        verbose_name_plural = "Careers"


# ------------------------------------------------------------
#
# store career and equipment type's relationship
#
# ------------------------------------------------------------
class career_equipments(models.Model):
    "Store career and equipment type's relationship."

    # careers's type
    career = models.ForeignKey("character_careers")

    # equipment's type
    equipment = models.ForeignKey("equipment_types")

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Career Equip Relation"
        verbose_name_plural = "Career Equip Relations"
        unique_together = ("career", "equipment")


# ------------------------------------------------------------
#
# store all NPCs
#
# ------------------------------------------------------------
class world_npcs(models.Model):
    "Store all NPCs."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=NAME_LENGTH)
    typeclass = models.ForeignKey("typeclasses")
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=KEY_LENGTH, blank=True)
    model = models.CharField(max_length=KEY_LENGTH)
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World NPC List"
        verbose_name_plural = "World NPC List"


# ------------------------------------------------------------
#
# store common characters
#
# ------------------------------------------------------------
class common_characters(models.Model):
    "Store common characters."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=NAME_LENGTH)
    typeclass = models.ForeignKey("typeclasses")
    desc = models.TextField(blank=True)
    model = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Common Character List"
        verbose_name_plural = "Common Character List"


# ------------------------------------------------------------
#
# store all skills
#
# ------------------------------------------------------------
class skills(models.Model):
    "Store all skills."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(max_length=NAME_LENGTH)
    typeclass = models.ForeignKey("typeclasses")
    desc = models.TextField(blank=True)
    cd = models.FloatField(blank=True, default=0)
    passive = models.BooleanField(blank=True, default=False)
    condition = models.TextField(blank=True)
    function = models.CharField(max_length=KEY_LENGTH)
    effect = models.FloatField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Skill"
        verbose_name_plural = "Skills"


# ------------------------------------------------------------
#
# store all quests
#
# ------------------------------------------------------------
class quests(models.Model):
    "Store all quests."

    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)
    name = models.CharField(blank=True, max_length=NAME_LENGTH)
    typeclass = models.ForeignKey("typeclasses")
    desc = models.TextField(blank=True)
    condition = models.TextField(blank=True)
    action = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest"
        verbose_name_plural = "Quests"


# ------------------------------------------------------------
#
# store quest objectives
#
# ------------------------------------------------------------
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


# ------------------------------------------------------------
#
# store quest dependency
#
# ------------------------------------------------------------
class quest_dependency(models.Model):
    "Store quest dependency."

    quest = models.ForeignKey("quests", db_index=True)
    dependency = models.ForeignKey("quests")
    type = models.IntegerField()

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest Dependency"
        verbose_name_plural = "Quest Dependency"


# ------------------------------------------------------------
#
# store event data
#
# ------------------------------------------------------------
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


# ------------------------------------------------------------
#
# store all dialogues
#
# ------------------------------------------------------------
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


# ------------------------------------------------------------
#
# store dialogue relations
#
# ------------------------------------------------------------
class dialogue_relations(models.Model):
    "Store dialogue relations."

    dialogue = models.ForeignKey("dialogues", db_index=True)
    next = models.ForeignKey("dialogues")

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Dialogue Relation"
        verbose_name_plural = "Dialogue Relations"


# ------------------------------------------------------------
#
# store dialogue sentences
#
# ------------------------------------------------------------
class dialogue_sentences(models.Model):
    "Store dialogue sentences."

    dialogue = models.ForeignKey("dialogues", db_index=True)
    ordinal = models.IntegerField()
    speaker = models.CharField(max_length=KEY_LENGTH, blank=True)
    content = models.TextField(blank=True)
    action = models.TextField(blank=True)
    provide_quest = models.ForeignKey("quests", null=True, blank=True)
    complete_quest = models.ForeignKey("quests", null=True, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Dialogue Sentence"
        verbose_name_plural = "Dialogue Sentences"


# ------------------------------------------------------------
#
# store npc's dialogue
#
# ------------------------------------------------------------
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


# ------------------------------------------------------------
#
# store dialogue quest dependency
#
# ------------------------------------------------------------
class dialogue_quest_dependency(models.Model):
    "Store dialogue quest dependency."

    dialogue = models.ForeignKey("dialogues", db_index=True)
    dependency = models.ForeignKey("quests")
    type = models.IntegerField()

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Dialogue Quest Dependency"
        verbose_name_plural = "Dialogue Quest Dependency"


# ------------------------------------------------------------
#
# character levels
#
# ------------------------------------------------------------
class character_models(models.Model):
    "Store all character level informations."

    character = models.CharField(max_length=KEY_LENGTH, db_index=True)
    level = models.IntegerField(blank=True, default=0)
    max_exp = models.IntegerField(blank=True, default=0)
    max_hp = models.IntegerField(blank=True, default=1)
    max_mp = models.IntegerField(blank=True, default=1)
    attack = models.IntegerField(blank=True, default=1)
    defence = models.IntegerField(blank=True, default=0)
    give_exp = models.IntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Character Level List"
        verbose_name_plural = "Character Level List"
        unique_together = ("character", "level")


# ------------------------------------------------------------
#
# character skills
#
# ------------------------------------------------------------
class character_skills(models.Model):
    "Store all character skill informations."

    character = models.CharField(max_length=KEY_LENGTH, db_index=True)
    skill = models.ForeignKey("skills")

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Character Skill List"
        verbose_name_plural = "Character Skill List"
        unique_together = ("character", "skill")


# ------------------------------------------------------------
#
# event mobs
#
# ------------------------------------------------------------
class event_mobs(models.Model):
    "Store all event mobs."

    key = models.CharField(max_length=KEY_LENGTH, db_index=True)
    mob = models.CharField(max_length=KEY_LENGTH)
    level = models.IntegerField()
    odds = models.FloatField(blank=True, default=0)
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Event Mob"
        verbose_name_plural = "Event Mobs"


# ------------------------------------------------------------
#
# event dialogues
#
# ------------------------------------------------------------
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


# ------------------------------------------------------------
#
# local strings
#
# ------------------------------------------------------------
class localized_strings(models.Model):
    "Store all server local strings informations."

    origin = models.TextField()
    local = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Server Local String"
        verbose_name_plural = "Server Local Strings"
