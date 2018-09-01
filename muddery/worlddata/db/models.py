
from __future__ import print_function

import re
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings


KEY_LENGTH = 255
NAME_LENGTH = 80
TYPECLASS_LENGTH = 80
POSITION_LENGTH = 80
VALUE_LENGTH = 80
CONDITION_LENGTH = 255

re_attribute_key = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


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

    # Show room's box if it does not have an icon.
    map_room_box = models.BooleanField(blank=True, default=False)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Game Setting"
        verbose_name_plural = "Game Settings"


# ------------------------------------------------------------
#
# Objects
#
# ------------------------------------------------------------
class BaseObjects(models.Model):
    """
    The base model of all objects.
    """
    # object's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # object's typeclass
    typeclass = models.CharField(max_length=KEY_LENGTH)

    # object's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True)
    
    # object's description for display
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"

    def __unicode__(self):
        return self.name + " (" + self.key + ")"


class world_areas(BaseObjects):
    "The game map is composed by areas."

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
        app_label = "worlddata"
        verbose_name = "World Area"
        verbose_name_plural = "World Areas"


class world_rooms(BaseObjects):
    "Defines all unique rooms."
    
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
        app_label = "worlddata"
        verbose_name = "Room"
        verbose_name_plural = "Rooms"


class world_exits(BaseObjects):
    "Defines all unique exits."

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
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Exit"
        verbose_name_plural = "Exits"


class world_objects(BaseObjects):
    "Store all unique objects."

    # The key of a world room.
    # object's location, it must be a room
    location = models.CharField(max_length=KEY_LENGTH)
    
    # Action's name
    action = models.CharField(max_length=NAME_LENGTH, blank=True)

    # the condition for showing the object
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    # object's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "World Object"
        verbose_name_plural = "World Objects"


class common_objects(BaseObjects):
    "Store all common objects."

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
        app_label = "worlddata"
        verbose_name = "Common Object"
        verbose_name_plural = "Common Objects"


class foods(common_objects):
    "Foods inherit from common objects."

    # Attributes. Value's type must be a python default value type.
    attr_1 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_2 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_3 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_4 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_5 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_6 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_7 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_8 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_9 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_10 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Food"
        verbose_name_plural = "Foods"


class skill_books(common_objects):
    "Skill books inherit from common objects."

    # skill's key
    skill = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Skill Book"
        verbose_name_plural = "Skill Books"


class equipments(common_objects):
    "equipments inherit from common objects."

    # The key of an equipment position.
    # equipment's position
    position = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of an equipment type.
    # equipment's type
    type = models.CharField(max_length=KEY_LENGTH)

    # Attributes. Value's type must be a python default value type.
    attr_1 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_2 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_3 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_4 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_5 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_6 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_7 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_8 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_9 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_10 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Equipment"
        verbose_name_plural = "Equipments"


class world_npcs(BaseObjects):
    "Store all NPCs."

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
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    # NPC's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "World NPC"
        verbose_name_plural = "World NPCs"


class common_characters(BaseObjects):
    "Store common characters."

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
        app_label = "worlddata"
        verbose_name = "Common Character List"
        verbose_name_plural = "Common Character List"


class shops(BaseObjects):
    "Store all shops."

    # the verb to open the shop
    verb = models.CharField(max_length=NAME_LENGTH, blank=True)

    # condition of the shop
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    # shop's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Shop"
        verbose_name_plural = "Shops"


class shop_goods(BaseObjects):
    "All goods that sold in shops."

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
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Shop Object"
        verbose_name_plural = "Shop Objects"


class skills(BaseObjects):
    "Store all skills."

    # skill's message when casting
    message = models.TextField(blank=True)

    # skill's cd
    cd = models.FloatField(blank=True, default=0)

    # if it is a passive skill
    passive = models.BooleanField(blank=True, default=False)

    # skill function's name
    function = models.CharField(max_length=KEY_LENGTH, blank=True)

    # skill's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    # skill's main type, used in autocasting skills.
    main_type = models.CharField(max_length=KEY_LENGTH, blank=True)

    # skill's sub type, used in autocasting skills.
    sub_type = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Skill"
        verbose_name_plural = "Skills"


class quests(BaseObjects):
    "Store all quests."

    # the condition to accept this quest.
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    # will do this action after a quest completed
    action = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Quest"
        verbose_name_plural = "Quests"


# ------------------------------------------------------------
#
# Objects additional data.
#
# ------------------------------------------------------------
class BaseAdditionalData(models.Model):
    """
    The base model of object's additinal data.
    """
    # object's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


# ------------------------------------------------------------
#
# exit lock's additional data
#
# ------------------------------------------------------------
class exit_locks(BaseAdditionalData):
    "Locked exit's additional data"

    # condition of the lock
    unlock_condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    # action to unlock the exit (optional)
    unlock_verb = models.CharField(max_length=NAME_LENGTH, blank=True)

    # description when locked
    locked_desc = models.TextField(blank=True)

    # if the exit can be unlocked automatically
    auto_unlock = models.BooleanField(blank=True, default=False)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Exit Lock"
        verbose_name_plural = "Exit Locks"


# ------------------------------------------------------------
#
# two way exit's additional data
#
# ------------------------------------------------------------
class two_way_exits(BaseAdditionalData):
    "Two way exit's additional data"

    # reverse exit's name
    reverse_name = models.CharField(max_length=NAME_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Two Way Exit"
        verbose_name_plural = "Two Way Exits"


# ------------------------------------------------------------
#
# object creator's additional data
#
# ------------------------------------------------------------
class object_creators(BaseAdditionalData):
    "Players can get new objects from an object_creator."
    
    # related object's key
    relation = models.CharField(max_length=KEY_LENGTH, db_index=True, blank=True)

    # loot's verb
    loot_verb = models.CharField(max_length=NAME_LENGTH, blank=True)

    # loot's condition
    loot_condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
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
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
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
        app_label = "worlddata"
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
        app_label = "worlddata"
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
        app_label = "worlddata"
        verbose_name = "Quest's reward List"
        verbose_name_plural = "Quest's reward Lists"
        unique_together = ("provider", "object")


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
        app_label = "worlddata"
        verbose_name = "Equipment's Position"
        verbose_name_plural = "Equipment's Positions"

    def __unicode__(self):
        return self.name

        
# ------------------------------------------------------------
#
# attribute's information
#
# ------------------------------------------------------------
class attributes_info(models.Model):
    "attributes's information"
    
    # attribute db field's name. It must be a attribute field name in character models.
    field = models.CharField(max_length=KEY_LENGTH, unique=True)
    
    # attribute's key, chars and numbers only.
    key = models.CharField(max_length=KEY_LENGTH, blank=True)
    
    # attribute's readable name.
    name = models.CharField(max_length=KEY_LENGTH, blank=True)
    
    # attribute's desc
    desc = models.TextField(blank=True)
    
    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Attrubute Information"
        verbose_name_plural = "Attribute Information"
        
    def clean(self):
        if self.key:
            if not re.match(re_attribute_key, self.key):
                error = ValidationError("Keys can only contain letters, numbers and underscores and must begin with a letter or an underscore.")
                raise ValidationError({"key": error})
        

# ------------------------------------------------------------
#
# Character attribute's information.
#
# ------------------------------------------------------------
class character_attributes_info(attributes_info):
    "Character's all available attributes"
    
    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Character Attrubute Information"
        verbose_name_plural = "Character Attribute Information"
        
        
# ------------------------------------------------------------
#
# Equipment attribute's information.
#
# ------------------------------------------------------------
class equipment_attributes_info(attributes_info):
    "Equipment's all available attributes"
    
    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Equipment Attrubute Information"
        verbose_name_plural = "Equipment Attribute Information"
        
        
# ------------------------------------------------------------
#
# Food attribute's information.
#
# ------------------------------------------------------------
class food_attributes_info(attributes_info):
    "Food's all available attributes"
    
    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Food Attrubute Information"
        verbose_name_plural = "Food Attribute Information"


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

    # max hp of the character
    max_hp = models.PositiveIntegerField(blank=True, default=1)
    
    # If a character's exp is larger than max_exp, the character can upgrade.
    # If max_exp is 0, the character can not upgrade any more.
    max_exp = models.PositiveIntegerField(blank=True, default=0)

    # exp provided to the character who killed this character
    give_exp = models.IntegerField(blank=True, default=0)

    # Attributes. Value's type must be a python default value type.
    attr_1 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_2 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_3 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_4 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_5 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_6 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_7 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_8 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_9 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    attr_10 = models.CharField(max_length=VALUE_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Character Model"
        verbose_name_plural = "Character Models"
        unique_together = ("key", "level")

    def __unicode__(self):
        return self.name + " (Lv" + str(self.level) + ")"


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
        app_label = "worlddata"
        verbose_name = "Character's Default Object"
        verbose_name_plural = "Character's Default Objects"
        unique_together = ("character", "object")


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
        app_label = "worlddata"
        verbose_name = "NPC Shop"
        verbose_name_plural = "NPC Shops"
        unique_together = ("npc", "shop")


# ------------------------------------------------------------
#
# skill types
#
# ------------------------------------------------------------
class skill_types(models.Model):
    """
    Skill's type, used in skill's main_type and sub_type. The type discribes the usage of a
    skill, which is useful in auto casting skills.
    """
    # type's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # the readable name of the skill type
    name = models.CharField(max_length=NAME_LENGTH, unique=True)
    
    # skill type's description
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Skill's Type"
        verbose_name_plural = "Skill's Types"

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
        app_label = "worlddata"
        verbose_name = "Character's Skill"
        verbose_name_plural = "Character's Skills"
        unique_together = ("character", "skill")


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
        app_label = "worlddata"
        verbose_name = "Quest Objective"
        verbose_name_plural = "Quest Objectives"
        unique_together = ("quest", "ordinal")


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
        app_label = "worlddata"
        verbose_name = "Quest Dependency"
        verbose_name_plural = "Quest Dependency"


# ------------------------------------------------------------
#
# store event data
#
# ------------------------------------------------------------
class event_data(models.Model):
    "Store event data."

    # event's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # trigger's relative object's key
    trigger_obj = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The type of the event trigger.
    # event's trigger
    trigger_type = models.CharField(max_length=KEY_LENGTH)

    # The type of an event action.
    # event's action
    action = models.CharField(max_length=KEY_LENGTH)

    # This event can only trigger one time.
    one_time = models.BooleanField(blank=True, default=False)

    # The odds of this event.
    odds = models.FloatField(blank=True, default=1.0)

    # the condition to enable this event
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
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
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # dialogue's name
    name = models.CharField(max_length=NAME_LENGTH, default="")

    # condition to show this dialogue
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
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
        app_label = "worlddata"
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
        app_label = "worlddata"
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
        app_label = "worlddata"
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
        app_label = "worlddata"
        verbose_name = "NPC Dialogue"
        verbose_name_plural = "NPC Dialogues"


# ------------------------------------------------------------
#
# event's data
#
# ------------------------------------------------------------
class BaseEventData(models.Model):
    # The key of an event.
    event_key = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


# ------------------------------------------------------------
#
# event attack's data
#
# ------------------------------------------------------------
class event_attacks(BaseEventData):
    "event attack's data"

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
        app_label = "worlddata"
        verbose_name = "Event Mob"
        verbose_name_plural = "Event Mobs"
        unique_together = ("event_key", "mob")


# ------------------------------------------------------------
#
# event dialogues
#
# ------------------------------------------------------------
class event_dialogues(BaseEventData):
    "Store all event dialogues."

    # The key of a dialogue.
    # dialogue's key
    dialogue = models.CharField(max_length=KEY_LENGTH)

    # The key of an NPC.
    # NPC's key
    npc = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Event Dialogues"
        verbose_name_plural = "Event Dialogues"
        unique_together = ("event_key", "dialogue")

        
# ------------------------------------------------------------
#
# condition descriptions
#
# ------------------------------------------------------------
class condition_desc(models.Model):
    "Object descriptions in different conditions."

    # The key of an object.
    key = models.CharField(max_length=KEY_LENGTH)

    # condition
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)
    
    # exit's description for display
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Condition Description"
        verbose_name_plural = "Condition Descriptions"
        unique_together = ("key", "condition")


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
        app_label = "worlddata"
        verbose_name = "Localized String"
        verbose_name_plural = "Localized Strings"


# ------------------------------------------------------------
#
# set image resources
#
# ------------------------------------------------------------
class image_resources(models.Model):
    "Store resource's information."

    # image's path
    resource = models.CharField(max_length=KEY_LENGTH, unique=True)

    # image's type
    type = models.CharField(max_length=KEY_LENGTH)

    # resource'e width
    image_width = models.PositiveIntegerField(blank=True, default=0)
    
    # resource'e height
    image_height = models.PositiveIntegerField(blank=True, default=0)
    
    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        verbose_name = "Image Resource"
        verbose_name_plural = "Image Resources"

    def __unicode__(self):
        return self.resource
