
from __future__ import print_function

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings


KEY_LENGTH = 255
NAME_LENGTH = 80
TYPECLASS_LENGTH = 80
POSITION_LENGTH = 80


def auto_generate_key(model):
    if not model.key:
        index = 0
        if model.id is not None:
            # Get this record's id.
            index = model.id
        else:
            try:
                # Get last id.
                query = model.__class__.objects.last()
                index = int(query.id)
                index += 1
            except Exception, e:
                pass

        model.key = model.__class__.__name__ + "_" + str(index)


def validate_object_key(model):
    """
    Check if the key exists. Object's key should be unique in all objects.
    """
    # Get models.
    from muddery.worlddata.data_sets import DATA_SETS
    for data_settings in DATA_SETS.object_data:
        if data_settings.model_name == model.__class__.__name__:
            # Models will validate unique values of its own,
            # so we do not validate them here.
            continue

        try:
            data_settings.model.objects.get(key=model.key)
        except Exception, e:
            continue

        error = ValidationError("The key '%(value)s' already exists in model %(model)s.",
                                code="unique",
                                params={"value": model.key, "model": data_settings.model_name})
        raise ValidationError({"key": error})

# ------------------------------------------------------------
#
# System data flag.
#
# ------------------------------------------------------------
class SystemData(models.Model):
    """
    All system data should have this flag. This flag is used to
    differentiate between system data and custom data.
    """
    # data's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # is system data or not
    system_data = models.BooleanField(blank=True, default=False)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "System Data"
        verbose_name_plural = "System Data"


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

    # The name of your game.
    game_name = models.CharField(max_length=NAME_LENGTH, blank=True)

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

    # Allow players to give up quests.
    can_give_up_quests = models.BooleanField(blank=True, default=True)

    # can close dialogue box or not.
    can_close_dialogue = models.BooleanField(blank=True, default=False)

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

    # Map's scale
    map_scale = models.FloatField(blank=True,
                                  default=75.0,
                                  validators=[MinValueValidator(0.0)])

    # Room's pixel size on the map.
    map_room_size = models.FloatField(blank=True,
                                      default=40.0,
                                      validators=[MinValueValidator(0.0)])

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Game Setting"
        verbose_name_plural = "Game Settings"


# ------------------------------------------------------------
#
# store all typeclasses
#
# ------------------------------------------------------------
class class_categories(SystemData):
    """
    Typeclass's category defines base types.

    The key is category's key.
    """

    # the readable name of the category
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    # category's description (optional)
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Class Category"
        verbose_name_plural = "Class Categories"

    def __unicode__(self):
        return self.name


# ------------------------------------------------------------
#
# store all typeclasses
#
# ------------------------------------------------------------
class typeclasses(SystemData):
    """
    Defines all available typeclasses.

    The key is typeclass's key.
    """

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
# world areas
#
# ------------------------------------------------------------
class world_areas(models.Model):
    "The game map is composed by areas."

    # area's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)
    
    # The key of a area typeclass.
    # area's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # area's name
    name = models.CharField(max_length=NAME_LENGTH, default="")
    
    # area's description for display
    desc = models.TextField(blank=True)

    # area's map background image resource
    background = models.CharField(max_length=KEY_LENGTH, blank=True)
    
    # Corresponding data are used to define the background image's position.
    # The corresponding map position will be shown on this point.
    background_point = models.CharField(max_length=POSITION_LENGTH, blank=True)
    
    # corresponding map position which matches the area background position
    corresp_map_pos = models.CharField(max_length=POSITION_LENGTH, blank=True)
    
    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "World Area"
        verbose_name_plural = "World Areas"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"

    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)


# ------------------------------------------------------------
#
# store all rooms
#
# ------------------------------------------------------------
class world_rooms(models.Model):
    "Defines all unique rooms."

    # room's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # The key of a room typeclass.
    # room's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # room's name for display
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # room's description for display
    desc = models.TextField(blank=True)
    
    # players can not fight in peaceful romms
    peaceful = models.BooleanField(blank=True, default=False)

    # The key of a world area.
    # The room's location, it must be a area.
    location = models.CharField(max_length=KEY_LENGTH, blank=True)

    # room's position which is used in maps
    position = models.CharField(max_length=POSITION_LENGTH, blank=True)

    # room's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)
    
    # room's background image resource
    background = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"
        
    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)


# ------------------------------------------------------------
#
# store all exits
#
# ------------------------------------------------------------
class world_exits(models.Model):
    "Defines all unique exits."

    # exit's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # The key of an exit typeclass.
    # exit's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # exit's name for display
    # If it's empty, use the destination room's name.
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

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

    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)


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
# two way exit's additional data
#
# ------------------------------------------------------------
class two_way_exits(models.Model):
    "Two way exit's additional data"

    # The key of a world exit.
    # related exit
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # reverse exit's name
    reverse_name = models.CharField(max_length=NAME_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Two Way Exit"
        verbose_name_plural = "Two Way Exits"

# ------------------------------------------------------------
#
# store all objects
#
# ------------------------------------------------------------
class world_objects(models.Model):
    "Store all unique objects."

    # object's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # The key of an object typeclass.
    # object's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # object's name
    name = models.CharField(max_length=NAME_LENGTH)

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

    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)
        

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
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # The key of an object typeclass.
    # object's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # object's name for display
    name = models.CharField(max_length=NAME_LENGTH)

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

    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)


# ------------------------------------------------------------
#
# store all foods
#
# ------------------------------------------------------------
class foods(common_objects):
    "Foods inherit from common objects."

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
# store all skill books
#
# ------------------------------------------------------------
class skill_books(common_objects):
    "Skill books inherit from common objects."

    # skill's key
    skill = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Skill Book"
        verbose_name_plural = "Skill Books"


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
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # The key of a character typeclass.
    # NPC's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # NPC's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # NPC's description for display
    desc = models.TextField(blank=True)

    # The key of a world room.
    # NPC's location, it must be a room.
    location = models.CharField(max_length=KEY_LENGTH)

    # NPC's model. If it is empty, will use NPC's key as its model.
    model = models.CharField(max_length=KEY_LENGTH, blank=True)

    # NPC's level
    level = models.PositiveIntegerField(blank=True, default=1)
    
    # Reborn time. The time of reborn after this character was killed. 0 means never reborn.
    reborn_time = models.PositiveIntegerField(blank=True, default=0)

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

    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)


# ------------------------------------------------------------
#
# store common characters
#
# ------------------------------------------------------------
class common_characters(models.Model):
    "Store common characters."

    # Character's key.
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # The key of a character typeclass.
    # Character's typeclass.
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # Character's name for display.
    name = models.CharField(max_length=NAME_LENGTH)

    # Character's description for display.
    desc = models.TextField(blank=True)

    # Character's model. If it is empty, character's key will be used as its model.
    model = models.CharField(max_length=KEY_LENGTH)

    # Character's level.
    level = models.PositiveIntegerField(blank=True, default=1)
    
    # Reborn time. The time of reborn after this character was killed. 0 means never reborn.
    reborn_time = models.PositiveIntegerField(blank=True, default=0)

    # Character's icon resource.
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Common Character List"
        verbose_name_plural = "Common Character List"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"

    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)

        # check model and level
        from muddery.worlddata.data_sets import DATA_SETS

        try:
            DATA_SETS.character_models.objects.get(key=self.model, level=self.level)
        except Exception, e:
            message = "Can not get this level's data."
            levels = DATA_SETS.character_models.objects.filter(key=self.model)
            available = [str(level.level) for level in levels]
            if len(available) == 1:
                message += " Available level: " + available[0]
            elif len(available) > 1:
                message += " Available levels: " + ", ".join(available)
            raise ValidationError({"level": message})


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
# shops
#
# ------------------------------------------------------------
class shops(models.Model):
    "Store all shops."

    # shop's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # The key of a shop typeclass.
    # Shop's typeclass.
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # shop's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # shop's description for display
    desc = models.TextField(blank=True)

    # the verb to open the shop
    verb = models.CharField(max_length=NAME_LENGTH, blank=True)

    # condition of the shop
    condition = models.TextField(blank=True)

    # shop's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Shop"
        verbose_name_plural = "Shops"

    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)


# ------------------------------------------------------------
#
# shop goods
#
# ------------------------------------------------------------
class shop_goods(models.Model):
    "All goods that sold in shops."

    # goods's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # the typeclass of this goods
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # shop's key
    shop = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # the key of objects to sell
    goods = models.CharField(max_length=KEY_LENGTH)

    # number of shop goods
    number = models.PositiveIntegerField(blank=True, default=1)

    # the price of the goods
    price = models.PositiveIntegerField(blank=True, default=1)

    # the unit of the goods price
    unit = models.CharField(max_length=KEY_LENGTH)

    # visible condition of the goods
    condition = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Shop Object"
        verbose_name_plural = "Shop Objects"

    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)


# ------------------------------------------------------------
#
# store npc's shop
#
# ------------------------------------------------------------
class npc_shops(models.Model):
    "Store npc's shops."

    # The key of an NPC.
    # NPC's key
    npc = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of a shop.
    # shop's key
    shop = models.CharField(max_length=KEY_LENGTH, db_index=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "NPC Shop"
        verbose_name_plural = "NPC Shops"
        unique_together = ("npc", "shop")


# ------------------------------------------------------------
#
# store all skills
#
# ------------------------------------------------------------
class skills(models.Model):
    "Store all skills."

    # skill's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # The key of a skill typeclass.
    # skill's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # skill's name for display
    name = models.CharField(max_length=NAME_LENGTH)

    # skill's description for display
    desc = models.TextField(blank=True)

    # skill's message when casting
    message = models.TextField(blank=True)

    # skill's cd
    cd = models.FloatField(blank=True, default=0)

    # if it is a passive skill
    passive = models.BooleanField(blank=True, default=False)

    # skill function's name
    function = models.CharField(max_length=KEY_LENGTH, blank=True)

    # Skill's icon resource.
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"

    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)


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
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # The key of a quest typeclass.
    # quest's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # quest's name for display
    name = models.CharField(max_length=NAME_LENGTH)

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

    def clean(self):
        auto_generate_key(self)
        validate_object_key(self)


# ------------------------------------------------------------
#
# quest objective's type
#
# ------------------------------------------------------------
class quest_objective_types(SystemData):
    """
    quest objective's type

    The key is type's key. It must be the values in utils.defines.
    """

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
class quest_dependency_types(SystemData):
    """
    quest dependency's type"

    The key is dependency's key. It must be the values in utils.defines.
    """

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
class event_types(SystemData):
    """
    event's type

    The key is event's key. It must be the values in utils.defines.
    """

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
class event_trigger_types(SystemData):
    """
    event trigger's type

    The key is type's key. It must be the values in utils.defines.
    """

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
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

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

    def clean(self):
        auto_generate_key(self)


# ------------------------------------------------------------
#
# store all dialogues
#
# ------------------------------------------------------------
class dialogues(models.Model):
    "Store all dialogues."

    # dialogue's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

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

    def clean(self):
        auto_generate_key(self)
        

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

    # speaker's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

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
# localized strings
#
# ------------------------------------------------------------
class localized_strings(models.Model):
    "Store all localized strings."

    # is system data or not
    system_data = models.BooleanField(blank=True, default=False)
    
    # word's category
    category = models.CharField(max_length=KEY_LENGTH, blank=True)

    # the origin words
    origin = models.TextField()

    # translated worlds
    local = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Localized String"
        verbose_name_plural = "Localized Strings"


# ------------------------------------------------------------
#
# set image resources
#
# ------------------------------------------------------------
class ImageResources(models.Model):
    "Store resource's information."

    # The key of image.
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # image's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # resource'e width
    image_width = models.PositiveIntegerField(null=True, blank=True)
    
    # resource'e height
    image_height = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Resource"
        verbose_name_plural = "Resources"

    def clean(self):
        auto_generate_key(self)


# ------------------------------------------------------------
#
# image resources
#
# ------------------------------------------------------------
class image_resources(ImageResources):
    "Store image resource's information."

    # resource    
    resource = models.ImageField(upload_to=settings.IMAGE_RESOURCE_DIR, null=True, blank=True, width_field='image_width', height_field='image_height')

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Image Resource"
        verbose_name_plural = "Image Resources"

    def __unicode__(self):
        return self.key + " (" + self.resource + ")"

# ------------------------------------------------------------
#
# icon resources
#
# ------------------------------------------------------------
class icon_resources(ImageResources):
    "Store icon resource's information."

    # resource    
    resource = models.ImageField(upload_to=settings.ICON_RESOURCE_DIR, null=True, blank=True, width_field='image_width', height_field='image_height')

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Icon Resource"
        verbose_name_plural = "Icon Resources"

    def __unicode__(self):
        return self.key + " (" + self.resource + ")"
