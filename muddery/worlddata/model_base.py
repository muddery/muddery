from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

KEY_LENGTH = 255
NAME_LENGTH = 20
TYPECLASS_LENGTH = 80
POSITION_LENGTH = 80


# ------------------------------------------------------------
#
# Game's basic settings.
#
# ------------------------------------------------------------
class game_settings(models.Model):
    """
    Game's basic settings.
    NOTE: Only uses the first record!
    """

    # The screen shows to players who are not loggin.
    connection_screen = models.TextField(blank=True)

    # In solo mode, a player can not see or affect other players.
    solo_mode = models.BooleanField(blank=True, default=False)

    # Time of global CD.
    global_cd = models.FloatField(blank=True,
                                  default=1.0,
                                  validators=[MinValueValidator(0.0)])

    # The CD of auto casting a skill. It must be bigger than GLOBAL_CD
    # They can not be equal!
    auto_cast_skill_cd = models.FloatField(blank=True,
                                           default=1.5,
                                           validators=[MinValueValidator(0.0)])

    # Player's reborn time after being killed. If it is below 0, players will be reborn immediately.
    player_reborn_cd = models.FloatField(blank=True,
                                         default=10.0,
                                         validators=[MinValueValidator(0.0)])

    # NPC's reborn time after being killed. If it is below 0, NPCs will not be reborn.
    npc_reborn_cd = models.FloatField(blank=True,
                                      default=10.0,
                                      validators=[MinValueValidator(0.0)])

    # Allow players to give up quests.
    can_give_up_quests = models.BooleanField(blank=True, default=True)

    # Send one dialogue to the client a time.
    single_dialogue_sentence = models.BooleanField(blank=True, default=True)

    # Can resume unfinished dialogues automatically.
    auto_resume_dialogues = models.BooleanField(blank=True, default=True)

    # The key of a world room.
    # It is the default home location used for all objects. This is used as a
    # fallback if an object's normal home location is deleted. It is the
    # key of the room. If it is empty, the home will be set to the first
    # room in WORLD_ROOMS.
    default_home_key = models.CharField(max_length=KEY_LENGTH, blank=True)

    # The key of a world room.
    # The start position for new characters. It is the key of the room.
    # If it is empty, the home will be set to the first room in WORLD_ROOMS.
    start_location_key = models.CharField(max_length=KEY_LENGTH, blank=True)

    # The key of a world room.
    # Player's default home. When a player dies, he will be moved to his home.
    default_player_home_key = models.CharField(max_length=KEY_LENGTH, blank=True)

    # The key of a character.
    # Default character of players.
    default_player_character_key = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Game Setting"
        verbose_name_plural = "Game Settings"


# ------------------------------------------------------------
#
# Webclient's basic settings.
#
# ------------------------------------------------------------
class client_settings(models.Model):
    """
    Html webclient's basic settings.
    NOTE: The server only uses the first record!
    """

    # Game's title on the webclient.
    game_title = models.CharField(max_length=80)

    # Room's pixel size on the map.
    map_room_size = models.FloatField(blank=True,
                                      default=40.0,
                                      validators=[MinValueValidator(0.0)])

    # Map's scale
    map_scale = models.FloatField(blank=True,
                                  default=75.0,
                                  validators=[MinValueValidator(0.0)])

    # Show command box or not.
    show_command_box = models.BooleanField(blank=True, default=False)

    # can close dialogue box or not.
    can_close_dialogue = models.BooleanField(blank=True, default=False)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Webclient Setting"
        verbose_name_plural = "Webclient Settings"

# ------------------------------------------------------------
#
# store all typeclasses
#
# ------------------------------------------------------------
class class_categories(models.Model):
    "Typeclass's category defines base types."

    # category's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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
    "Defines all available typeclasses."

    # typeclass's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # the readable name of the typeclass
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    # the typeclass's path that related to a class
    path = models.CharField(max_length=TYPECLASS_LENGTH, blank=True)

    # The key of a typeclass category.
    # typeclass's category
    category = models.CharField(max_length=KEY_LENGTH)

    # typeclass's description (optional)
    desc = models.TextField(blank=True)
    
    # Can loot from objects of this type.
    can_loot = models.BooleanField(blank=True, default=False)

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
    "Defines all unique rooms."

    # room's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # room's name for display
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # The key of a room typeclass.
    # room's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # room's description for display
    desc = models.TextField(blank=True)

    # room's position which is used in maps
    position = models.CharField(max_length=POSITION_LENGTH, blank=True)
    
    # room's background image resource
    background = models.CharField(max_length=KEY_LENGTH, blank=True)

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
    "Defines all unique exits."

    # exit's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # exit's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # The key of an exit typeclass.
    # exit's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # exit's description for display
    desc = models.TextField(blank=True)

    # the action verb to enter the exit (optional)
    verb = models.CharField(max_length=NAME_LENGTH, blank=True)

    # The key of a world room.
    # The exit's location, it must be a room.
    # Players can see and enter an exit from this room.
    location = models.CharField(max_length=KEY_LENGTH)

    # The key of a world room.
    # The exits's destination.
    destination = models.CharField(max_length=KEY_LENGTH)

    # the condition to show the exit
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
    "Locked exit's additional data"

    # The key of a world exit.
    # related exit
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # object's name
    name = models.CharField(max_length=NAME_LENGTH)

    # The key of an object typeclass.
    # object's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # the object's destination
    desc = models.TextField(blank=True)

    # The key of a world room.
    # object's location, it must be a room
    location = models.CharField(max_length=KEY_LENGTH)

    # the condition for showing the object
    condition = models.TextField(blank=True)
    
    # object's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

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
    "Players can get new objects from an object_creator."

    # The key of a world object.
    # related object
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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
    "Loot list. It is used in object_creators and mods."

    # the provider of the object
    provider = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # the key of dropped object
    object = models.CharField(max_length=KEY_LENGTH)

    # number of dropped object
    number = models.PositiveIntegerField(blank=True, default=0)

    # odds of drop, from 0.0 to 1.0
    odds = models.FloatField(blank=True, default=0)

    # The key of a quest.
    # if it is not empty, the player must have this quest, or will not drop
    quest = models.CharField(max_length=KEY_LENGTH, blank=True)

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
# object creator's loot list
#
# ------------------------------------------------------------
class creator_loot_list(loot_list):
    "Store character's loot list."
    
    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Object Creator's Loot List"
        verbose_name_plural = "Object Creator's Loot Lists"
        unique_together = ("provider", "object")
        

# ------------------------------------------------------------
#
# character's loot list
#
# ------------------------------------------------------------
class character_loot_list(loot_list):
    "Store character's loot list."

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Character's Loot List"
        verbose_name_plural = "Character's Loot Lists"
        unique_together = ("provider", "object")


# ------------------------------------------------------------
#
# quest's rewards
#
# ------------------------------------------------------------
class quest_reward_list(loot_list):
    "Quest reward's list."
    
    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Quest's reward List"
        verbose_name_plural = "Quest's reward Lists"
        unique_together = ("provider", "object")


# ------------------------------------------------------------
#
# store all common objects
#
# ------------------------------------------------------------
class common_objects(models.Model):
    "Store all common objects."

    # object's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # object's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # The key of an object typeclass.
    # object's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # object's description for display
    desc = models.TextField(blank=True)

    # the max number of this object in one pile, must above 1
    max_stack = models.PositiveIntegerField(blank=True, default=1)

    # if can have only one pile of this object
    unique = models.BooleanField(blank=True, default=False)
    
    # if this object can be removed from the inventory when its number is decreased to zero.
    can_remove = models.BooleanField(blank=True, default=True)

    # if this object can discard
    can_discard = models.BooleanField(blank=True, default=True)

    # object's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

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
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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

    # The key of an equipment position.
    # equipment's position
    position = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of an equipment type.
    # equipment's type
    type = models.CharField(max_length=KEY_LENGTH)

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
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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

    # The key of a character career.
    # careers's type
    career = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of an equipment type.
    # equipment's type
    equipment = models.CharField(max_length=KEY_LENGTH)

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
    level = models.PositiveIntegerField(blank=True, default=1)

    # If a character's exp is larger than max_exp, the character can upgrade.
    # If max_exp is 0, the character can not upgrade any more.
    max_exp = models.PositiveIntegerField(blank=True, default=0)

    # max hp of the character
    max_hp = models.PositiveIntegerField(blank=True, default=1)

    # max mp of the character
    max_mp = models.PositiveIntegerField(blank=True, default=1)

    # attack value of the character
    attack = models.IntegerField(blank=True, default=1)

    # defence value of the character
    defence = models.IntegerField(blank=True, default=0)

    # exp provided to the character who killed this character
    give_exp = models.IntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Character Model"
        verbose_name_plural = "Character Models"
        unique_together = ("key", "level")

    def __unicode__(self):
        return self.name + " (Lv" + str(self.level) + ")"


# ------------------------------------------------------------
#
# store all NPCs
#
# ------------------------------------------------------------
class world_npcs(models.Model):
    "Store all NPCs."

    # NPC's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # NPC's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # The key of a character typeclass.
    # NPC's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # NPC's description for display
    desc = models.TextField(blank=True)

    # The key of a world room.
    # NPC's location, it must be a room.
    location = models.CharField(max_length=KEY_LENGTH)

    # NPC's model. If it is empty, will use NPC's key as its model.
    model = models.CharField(max_length=KEY_LENGTH, blank=True)

    # NPC's level
    level = models.PositiveIntegerField(blank=True, default=1)

    # the condition for showing the NPC
    condition = models.TextField(blank=True)
    
    # NPC's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

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
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # Character's name for display.
    name = models.CharField(max_length=NAME_LENGTH)

    # The key of a character typeclass.
    # Character's typeclass.
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # Character's description for display.
    desc = models.TextField(blank=True)

    # Character's model. If it is empty, character's key will be used as its model.
    model = models.CharField(max_length=KEY_LENGTH)

    # Character's level.
    level = models.PositiveIntegerField(blank=True, default=1)
    
    # Character's icon resource.
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Common Character List"
        verbose_name_plural = "Common Character List"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"


# ------------------------------------------------------------
#
# character's default objects
#
# ------------------------------------------------------------
class default_objects(models.Model):
    "character's default objects"

    # Character's model.
    character = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of an object.
    # Object's key.
    object = models.CharField(max_length=KEY_LENGTH)
    
    # Object's number
    number = models.PositiveIntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Character's Default Object"
        verbose_name_plural = "Character's Default Objects"
        unique_together = ("character", "object")


# ------------------------------------------------------------
#
# store all skills
#
# ------------------------------------------------------------
class skills(models.Model):
    "Store all skills."

    # skill's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # skill's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # The key of a skill typeclass.
    # skill's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

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

    # Skill's icon resource.
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)
    
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

    # character's model
    character = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of a skill.
    # skill's key
    skill = models.CharField(max_length=KEY_LENGTH)

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
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # quest's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # The key of a quest typeclass.
    # quest's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # quest's description for display
    desc = models.TextField(blank=True)

    # the condition to accept this quest.
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

    # Type's key. It must be the values in utils/defines.py.
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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

    # The key of a quest.
    # quest's key
    quest = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # objective's ordinal
    ordinal = models.IntegerField(blank=True, default=0)

    # The key of an objetive type.
    # objective's type
    type = models.CharField(max_length=KEY_LENGTH)

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

    # Dependency's key. It must be the values in utils/defines.pyl
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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

    # The key of a quest.
    # quest's key
    quest = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of a quest.
    # quest that dependends on
    dependency = models.CharField(max_length=KEY_LENGTH)

    # The key of a quest dependency type.
    # dependency's type
    type = models.CharField(max_length=KEY_LENGTH)

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

    # Event's key. It must be the values in utils/defines.py
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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

    # Type's key. It must be the values in utils/defines.py
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # the readable name of the event
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    # The key of an event type.
    # event's type
    type = models.CharField(max_length=KEY_LENGTH)

    # The key of an event trigger type.
    # event's trigger
    trigger_type = models.CharField(max_length=KEY_LENGTH)

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
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

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

    # The key of a dialogue.
    # dialogue's key
    dialogue = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of a quest.
    # related quest's key
    dependency = models.CharField(max_length=KEY_LENGTH)

    # The key of a quest dependency type.
    # dependency's type
    type = models.CharField(max_length=KEY_LENGTH)

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

    # The key of a dialogue.
    # dialogue's key
    dialogue = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of a dialogue.
    # next dialogue's key
    next_dlg = models.CharField(max_length=KEY_LENGTH, db_index=True)

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

    # The key of a dialogue.
    # dialogue's key
    dialogue = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # sentence's ordinal
    ordinal = models.IntegerField()

    # sentence's speaker
    speaker = models.CharField(max_length=NAME_LENGTH, blank=True)

    # sentence's content
    content = models.TextField(blank=True)

    # will do this action after this sentence
    action = models.TextField(blank=True)

    # The key of a quest.
    # can provide this quest
    provide_quest = models.CharField(max_length=KEY_LENGTH, blank=True)

    # The key of a quest.
    # can complete this quest
    complete_quest = models.CharField(max_length=KEY_LENGTH, blank=True)

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

    # The key of an NPC.
    # NPC's key
    npc = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of a dialogue.
    # dialogue's key
    dialogue = models.CharField(max_length=KEY_LENGTH, db_index=True)

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

    # The key of an event.
    # event's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # The key of a character.
    # mob's key
    mob = models.CharField(max_length=KEY_LENGTH)

    # mob's level
    level = models.PositiveIntegerField()

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

    # The key of an event.
    # event's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # The key of a dialogue.
    # dialogue's key
    dialogue = models.CharField(max_length=KEY_LENGTH)

    # The key of an NPC.
    # NPC's key
    npc = models.CharField(max_length=KEY_LENGTH, blank=True)

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

    # word's category
    category = models.TextField(blank=True)

    # the origin words
    origin = models.TextField()

    # translated worlds
    local = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Server Local String"
        verbose_name_plural = "Server Local Strings"


# ------------------------------------------------------------
#
# image resources
#
# ------------------------------------------------------------
class image_resources(models.Model):
    "Store image resource's information."

    # The key of image.
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # image's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True, default="")

    # resource    
    resource = models.ImageField(upload_to=settings.IMAGE_RESOURCE_DIR, null=True, blank=True, width_field='image_width', height_field='image_height')

    # resource'e width
    image_width = models.PositiveIntegerField(null=True, blank=True)
    
    # resource'e height
    image_height = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Image Resource"
        verbose_name_plural = "Image Resources"


# ------------------------------------------------------------
#
# icon resources
#
# ------------------------------------------------------------
class icon_resources(models.Model):
    "Store icon resource's information."

    # The key of icon.
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # icon's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True, default="")

    # resource    
    resource = models.ImageField(upload_to=settings.ICON_RESOURCE_DIR, null=True, blank=True, width_field='image_width', height_field='image_height')

    # resource'e width
    image_width = models.PositiveIntegerField(null=True, blank=True)
    
    # resource'e height
    image_height = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Icon Resource"
        verbose_name_plural = "Icon Resources"
