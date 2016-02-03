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
class class_categories(models.Model):
    "typeclass's category"

    # category's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # the readable name of the category
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    # category's description (optional)
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Class category"
        verbose_name_plural = "Class Categories"

    def __unicode__(self):
        return self.name


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

    # typeclass's category
    category = models.ForeignKey("class_categories")

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
        return self.name + " (" + self.key + ")"


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
        return self.name + " (" + self.key + ")"


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
        return self.name + " (" + self.key + ")"


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

    # the provider of the object. it is not a foreighkey because the provider can be in several tables.
    provider = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # the key of dropped object. it is not a foreighkey because the object can be from several tables.
    object = models.CharField(max_length=KEY_LENGTH)

    # number of dropped object
    number = models.IntegerField(blank=True, default=0)

    # odds of drop, from 0.0 to 1.0
    odds = models.FloatField(blank=True, default=0)

    # if it is not empty, the player must have this quest, or will not drop
    quest = models.ForeignKey("quests", null=True, blank=True)

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

    # object's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # object's typeclass
    typeclass = models.ForeignKey("typeclasses")

    # object's description for display
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

    def __unicode__(self):
        return self.name + " (" + self.key + ")"


# ------------------------------------------------------------
#
# store all foods
#
# ------------------------------------------------------------
class foods(common_objects):
    "foods inherit from common objects."

    # food's hp effect
    hp = models.IntegerField(blank=True, default=0)

    # food's mp effect
    mp = models.IntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Food"
        verbose_name_plural = "Foods"


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
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

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

    # position's name for display
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

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
    "equipments inherit from common objects."

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
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    # careers's description
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Career"
        verbose_name_plural = "Careers"

    def __unicode__(self):
        return self.name


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
# character models
#
# ------------------------------------------------------------
class character_models(models.Model):
    "Store all character level informations."

    # model's key
    key = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # model's name
    name = models.CharField(max_length=NAME_LENGTH)

    # model's level
    level = models.IntegerField(blank=True, default=1)

    # If a character's exp is larger than max_exp, the character can upgrade.
    # If max_exp is 0, the character can not upgrade any more.
    max_exp = models.IntegerField(blank=True, default=0)

    # max hp of the character
    max_hp = models.IntegerField(blank=True, default=1)

    # max mp of the character
    max_mp = models.IntegerField(blank=True, default=1)

    # attack value of the character
    attack = models.IntegerField(blank=True, default=1)

    # defence value of the character
    defence = models.IntegerField(blank=True, default=0)

    # exp provided to the character who killed this character
    give_exp = models.IntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Character Level"
        verbose_name_plural = "Character Levels"
        unique_together = ("key", "level")

    def __unicode__(self):
        return self.name + " (Lv" + self.level + ")"


# ------------------------------------------------------------
#
# store all NPCs
#
# ------------------------------------------------------------
class world_npcs(models.Model):
    "Store all NPCs."

    # NPC's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # NPC's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # NPC's typeclass
    typeclass = models.ForeignKey("typeclasses")

    # NPC's description for display
    desc = models.TextField(blank=True)

    # NPC's location, it must be a room.
    location = models.ForeignKey("world_rooms")

    # NPC's model. If it is empty, will use NPC's key as its model.
    model = models.CharField(max_length=KEY_LENGTH, blank=True)

    # NPC's level
    level = models.IntegerField(blank=True, default=1)

    # the condition for showing the NPC
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World NPC"
        verbose_name_plural = "World NPCs"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"


# ------------------------------------------------------------
#
# store common characters
#
# ------------------------------------------------------------
class common_characters(models.Model):
    "Store common characters."

    # Character's key.
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # Character's name for display.
    name = models.CharField(max_length=NAME_LENGTH)

    # Character's typeclass.
    typeclass = models.ForeignKey("typeclasses")

    # Character's description for display.
    desc = models.TextField(blank=True)

    # Character's model. If it is empty, will use character's key as its model.
    model = models.CharField(max_length=KEY_LENGTH)

    # Character's level
    level = models.IntegerField(blank=True, default=1)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Common Character List"
        verbose_name_plural = "Common Character List"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"

# ------------------------------------------------------------
#
# store all skills
#
# ------------------------------------------------------------
class skills(models.Model):
    "Store all skills."

    # skill's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # skill's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # skill's typeclass
    typeclass = models.ForeignKey("typeclasses")

    # skill's description for display
    desc = models.TextField(blank=True)

    # skill's cd
    cd = models.FloatField(blank=True, default=0)

    # if it is a passive skill
    passive = models.BooleanField(blank=True, default=False)

    # condition for cast this skill
    condition = models.TextField(blank=True)

    # skill function's name
    function = models.CharField(max_length=KEY_LENGTH)

    # skill's effect value
    effect = models.FloatField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"

# ------------------------------------------------------------
#
# character's default skills
#
# ------------------------------------------------------------
class default_skills(models.Model):
    "character's default skills"

    # character's key
    character = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # skill's key
    skill = models.ForeignKey("skills")

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Character's Skill"
        verbose_name_plural = "Character's Skills"
        unique_together = ("character", "skill")


# ------------------------------------------------------------
#
# store all quests
#
# ------------------------------------------------------------
class quests(models.Model):
    "Store all quests."

    # quest's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # quest's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # quest's typeclass
    typeclass = models.ForeignKey("typeclasses")

    # quest's description for display
    desc = models.TextField(blank=True)

    # the condition to accept this quest. TODO
    condition = models.TextField(blank=True)

    # will do this action after a quest completed
    action = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest"
        verbose_name_plural = "Quests"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"


# ------------------------------------------------------------
#
# quest objective's type
#
# ------------------------------------------------------------
class quest_objective_types(models.Model):
    "quest objective's type"

    # type's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # type's id, must be the values in utils/defines.py
    type_id = models.IntegerField()

    # the readable name of the type
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    # type's description (optional)
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest Objective's Type"
        verbose_name_plural = "Quest Objective's Types"

    def __unicode__(self):
        return self.name


# ------------------------------------------------------------
#
# store quest objectives
#
# ------------------------------------------------------------
class quest_objectives(models.Model):
    "Store all quest objectives."

    # quest's key
    quest = models.ForeignKey("quests")

    # objective's ordinal
    ordinal = models.IntegerField(blank=True, default=0)

    # objective's type
    type = models.ForeignKey("quest_objective_types")

    # relative object's key
    object = models.CharField(max_length=KEY_LENGTH, blank=True)

    # objective's number
    number = models.IntegerField(blank=True, default=0)

    # objective's discription for display
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest Objective"
        verbose_name_plural = "Quest Objectives"
        unique_together = ("quest", "ordinal")


# ------------------------------------------------------------
#
# quest dependency's type
#
# ------------------------------------------------------------
class quest_dependency_types(models.Model):
    "quest dependency's type"

    # dependency's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # dependency's id, must be the values in utils/defines.py
    type_id = models.IntegerField()

    # the readable name of the dependency
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    # dependency's description (optional)
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest dependency's Type"
        verbose_name_plural = "Quest dependency's Types"

    def __unicode__(self):
        return self.name


# ------------------------------------------------------------
#
# store quest dependencies
#
# ------------------------------------------------------------
class quest_dependencies(models.Model):
    "Store quest dependency."

    # quest's key
    quest = models.ForeignKey("quests")

    # quest that dependends on
    dependency = models.ForeignKey("quests")

    # dependency's type
    type = models.ForeignKey("quest_dependency_types")

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest Dependency"
        verbose_name_plural = "Quest Dependency"


# ------------------------------------------------------------
#
# event's type
#
# ------------------------------------------------------------
class event_types(models.Model):
    "event's type"

    # event's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # event's id, must be the values in utils/defines.py
    type_id = models.IntegerField()

    # the readable name of the event type
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    # event's description (optional)
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Event's Type"
        verbose_name_plural = "Event's Types"

    def __unicode__(self):
        return self.name


# ------------------------------------------------------------
#
# event trigger's types
#
# ------------------------------------------------------------
class event_trigger_types(models.Model):
    "event trigger's type"

    # type's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # type's id, must be the values in utils/defines.py
    type_id = models.IntegerField()

    # the readable name of the event trigger type
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    # type's description (optional)
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Event Trigger Type"
        verbose_name_plural = "Event Trigger Types"

    def __unicode__(self):
        return self.name


# ------------------------------------------------------------
#
# store event data
#
# ------------------------------------------------------------
class event_data(models.Model):
    "Store event data."

    # event's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # event's type
    type = models.ForeignKey("event_types")

    # event's trigger
    trigger_type = models.ForeignKey("event_trigger_types")

    # trigger's relative object's key
    trigger_obj = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # the condition to enable this event
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __unicode__(self):
        return self.key


# ------------------------------------------------------------
#
# store all dialogues
#
# ------------------------------------------------------------
class dialogues(models.Model):
    "Store all dialogues."

    # dialogue's key
    key = models.CharField(max_length=KEY_LENGTH, primary_key=True)

    # dialogue's name
    name = models.CharField(max_length=NAME_LENGTH, default="")

    # condition to show this dialogue
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Dialogue"
        verbose_name_plural = "Dialogues"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"


# ------------------------------------------------------------
#
# store dialogue quest dependencies
#
# ------------------------------------------------------------
class dialogue_quest_dependencies(models.Model):
    "Store dialogue quest dependencies."

    # dialogue's key
    dialogue = models.ForeignKey("dialogues")

    # related quest's key
    dependency = models.ForeignKey("quests")

    # dependency's type
    type = models.ForeignKey("quest_dependency_types")

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Dialogue Quest Dependency"
        verbose_name_plural = "Dialogue Quest Dependencies"


# ------------------------------------------------------------
#
# store dialogue relations
#
# ------------------------------------------------------------
class dialogue_relations(models.Model):
    "Store dialogue relations."

    # dialogue's key
    dialogue = models.ForeignKey("dialogues")

    # next dialogue's key
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

    # dialogue's key
    dialogue = models.ForeignKey("dialogues")

    # sentence's ordinal
    ordinal = models.IntegerField()

    # sentence's speaker
    speaker = models.CharField(max_length=NAME_LENGTH, blank=True)

    # sentence's content
    content = models.TextField(blank=True)

    # will do this action after this sentence
    action = models.TextField(blank=True)

    # can provide this quest
    provide_quest = models.ForeignKey("quests", null=True, blank=True)

    # can complete this quest
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

    # NPC's key
    npc = models.ForeignKey("world_npcs")

    # dialogue's key
    dialogue = models.ForeignKey("dialogues")

    # if it is a default dialogue
    default = models.BooleanField(blank=True, default=False)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "NPC Dialogue"
        verbose_name_plural = "NPC Dialogues"


# ------------------------------------------------------------
#
# event attack's data
#
# ------------------------------------------------------------
class event_attacks(models.Model):
    "event attack's data"

    # event's key
    key = models.OneToOneField("event_data")

    # mob's key
    mob = models.ForeignKey("common_characters")

    # mob's level
    level = models.IntegerField()

    # event's odds
    odds = models.FloatField(blank=True, default=0)

    # combat's description
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

    # event's key
    key = models.OneToOneField("event_data")

    # dialogue's key
    dialogue = models.ForeignKey("dialogues")

    # NPC's key
    npc = models.ForeignKey("world_npcs", null=True, blank=True)

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

    # the origin words
    origin = models.TextField()

    # translated worlds
    local = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Server Local String"
        verbose_name_plural = "Server Local Strings"
