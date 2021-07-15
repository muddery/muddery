
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
TEXT_CONTENT_LENGTH = 255

re_attribute_key = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


# ------------------------------------------------------------
#
# The game world system's data.
# Users should not modify it manually.
#
# ------------------------------------------------------------
class system_data(models.Model):
    """
    The game world system's data.
    """
    # The automatic index of objects.
    object_index = models.PositiveIntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


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
    auto_cast_skill_cd = models.PositiveIntegerField(blank=True, default=1)

    # Allow players to give up quests.
    can_give_up_quests = models.BooleanField(blank=True, default=True)

    # can close dialogue box or not.
    can_close_dialogue = models.BooleanField(blank=True, default=False)

    # Can resume unfinished dialogues automatically.
    auto_resume_dialogues = models.BooleanField(blank=True, default=True)

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

    # The key of a character.
    # Default character of staffs.
    default_staff_character_key = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


# ------------------------------------------------------------
#
# Game's basic settings.
#
# ------------------------------------------------------------
class honour_settings(models.Model):
    """
    honour combat's settings.
    NOTE: Only uses the first record!
    """
    # The minimum level that a player can attend a honour combat.
    min_honour_level = models.PositiveIntegerField(blank=True, default=1)

    # The number of top honour players that a player can see.
    top_rankings_number = models.PositiveIntegerField(blank=True, default=10)

    # The number of neighbor players on the honour list that a player can see.
    nearest_rankings_number = models.PositiveIntegerField(blank=True, default=10)

    # The number of neighbor players on the honour list that a player can fight.
    # honour_opponents_number = models.PositiveIntegerField(blank=True, default=100)

    # The maximum honour difference that the characters can match. 0 means no limits.
    max_honour_diff = models.PositiveIntegerField(blank=True, default=0)

    # The prepare time before starting a match. In seconds.
    preparing_time = models.PositiveIntegerField(blank=True, default=10)

    # The minimum time between two matches.
    match_interval = models.PositiveIntegerField(blank=True, default=10)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


# ------------------------------------------------------------
# Object's base
# ------------------------------------------------------------
class BaseObjects(models.Model):
    """
    The base model of all objects. All objects data are linked with keys.
    """
    # object's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"

    def __unicode__(self):
        return self.key


class objects(BaseObjects):
    """
    All objects.
    """
    # object's element type
    element_type = models.CharField(max_length=KEY_LENGTH)

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

    # area's element type
    element_type = models.CharField(max_length=KEY_LENGTH)

    # area's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # area's description for display
    desc = models.TextField(blank=True)

    # area's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    # area's map background image resource
    background = models.CharField(max_length=KEY_LENGTH, blank=True)

    # area's width
    width = models.PositiveIntegerField(blank=True, default=0)

    # area's height
    height = models.PositiveIntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


class world_rooms(BaseObjects):
    "Defines all unique rooms."

    # room's element type
    element_type = models.CharField(max_length=KEY_LENGTH)

    # room's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # room's description for display
    desc = models.TextField(blank=True)

    # room's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    # The key of a world area.
    # The room's location, it must be a area.
    area = models.CharField(max_length=KEY_LENGTH, blank=True, db_index=True)

    # players can not fight in peaceful romms
    peaceful = models.BooleanField(blank=True, default=False)

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


# ------------------------------------------------------------
#
# rooms that can give profits to characters in the room.
#
# ------------------------------------------------------------
class profit_rooms(BaseObjects):
    """
    The action to trigger other actions at interval.
    """
    # Repeat interval in seconds.
    interval = models.PositiveIntegerField(blank=True, default=0)

    # Can trigger events when the character is offline.
    offline = models.BooleanField(blank=True, default=False)

    # This message will be sent to the character when the interval begins.
    begin_message = models.TextField(blank=True)

    # This message will be sent to the character when the interval ends.
    end_message = models.TextField(blank=True)

    # the condition for getting profits
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


class world_objects(BaseObjects):
    "Store all unique objects."

    # The key of a world room.
    # object's location, it must be a room
    location = models.CharField(max_length=KEY_LENGTH, db_index=True)

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


class common_objects(BaseObjects):
    "Store all common objects."

    # object's element type
    element_type = models.CharField(max_length=KEY_LENGTH)

    # object's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # object's description for display
    desc = models.TextField(blank=True)

    # object's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


class pocket_objects(BaseObjects):
    "Store all pocket objects."

    # the max number of this object in one pile, must above 1
    max_stack = models.PositiveIntegerField(blank=True, default=1)

    # if can have only one pile of this object
    unique = models.BooleanField(blank=True, default=False)

    # if this object can be removed from the inventory when its number is decreased to zero.
    can_remove = models.BooleanField(blank=True, default=True)

    # if this object can discard
    can_discard = models.BooleanField(blank=True, default=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


class foods(BaseObjects):
    "Foods inherit from common objects."

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


class skill_books(BaseObjects):
    "Skill books inherit from common objects."

    # skill's key
    skill = models.CharField(max_length=KEY_LENGTH)

    # skill's level
    level = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


class equipments(BaseObjects):
    "equipments inherit from common objects."

    # The key of an equipment position.
    # equipment's position
    position = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of an equipment type.
    # equipment's type
    type = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


class characters(BaseObjects):
    "Store common characters."

    # object's element type
    element_type = models.CharField(max_length=KEY_LENGTH)

    # object's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # object's description for display
    desc = models.TextField(blank=True)

    # object's icon resource
    icon = models.CharField(max_length=KEY_LENGTH, blank=True)

    # Character's level.
    level = models.PositiveIntegerField(blank=True, default=1)

    # Reborn time. The time of reborn after this character was killed. 0 means never reborn.
    reborn_time = models.PositiveIntegerField(blank=True, default=0)

    # Friendly of this character.
    friendly = models.IntegerField(blank=True, default=0)

    # Clone another character's custom properties if this character's data is empty.
    clone = models.CharField(max_length=KEY_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


class world_npcs(BaseObjects):
    "Store all NPCs."

    # NPC's location, it must be a room.
    location = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # the condition for showing the NPC
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


class player_characters(BaseObjects):
    "Player's character."

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


class staff_characters(BaseObjects):
    "Staff's character."

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


# ------------------------------------------------------------
#
# exits connecting between rooms.
#
# ------------------------------------------------------------
class world_exits(models.Model):
    "Defines all unique exits."

    # object's key
    key = models.CharField(max_length=KEY_LENGTH, unique=True, blank=True)

    # object's element type
    element_type = models.CharField(max_length=KEY_LENGTH)

    # The exit's name.
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # The key of a world room.
    # The exit's location, it must be a room.
    # Players can see and enter an exit from this room.
    location = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of a world room.
    # The exits's destination.
    destination = models.CharField(max_length=KEY_LENGTH)

    # the action verb to enter the exit (optional)
    verb = models.CharField(max_length=NAME_LENGTH, blank=True)

    # the condition to show the exit
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


# ------------------------------------------------------------
#
# exit lock's additional data
#
# ------------------------------------------------------------
class exit_locks(BaseObjects):
    "Locked exit's additional data"

    # condition of the lock
    unlock_condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    # action to unlock the exit (optional)
    unlock_verb = models.CharField(max_length=NAME_LENGTH, blank=True)

    # description when locked
    locked_desc = models.TextField(blank=True)

    # description when unlocked
    unlocked_desc = models.TextField(blank=True)

    # if the exit can be unlocked automatically
    auto_unlock = models.BooleanField(blank=True, default=False)

    # when a character unlocked an exit, the exit is unlocked for this character forever.
    unlock_forever = models.BooleanField(blank=True, default=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


# ------------------------------------------------------------
#
# object creator's additional data
#
# ------------------------------------------------------------
class object_creators(BaseObjects):
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


class skills(models.Model):
    "Store all skills."

    # shop's key
    key = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # shop's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # shop's description
    desc = models.TextField(blank=True)

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


class shops(BaseObjects):
    "Store all shops."

    # object's element type
    element_type = models.CharField(max_length=KEY_LENGTH)

    # shop's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # shop's description
    desc = models.TextField(blank=True)

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


class shop_goods(models.Model):
    "All goods that sold in shops."

    # shop's key
    shop = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # the key of objects to sell
    goods = models.CharField(max_length=KEY_LENGTH)

    # goods level
    level = models.PositiveIntegerField(blank=True, null=True)

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

    # Can get another object after this one.
    multiple = models.BooleanField(blank=True, default=True)

    # This message will be sent to the character when get objects.
    message = models.TextField(blank=True)

    # The key of a quest.
    # if it is not empty, the player must have this quest but not accomplish this quest.
    quest = models.CharField(max_length=KEY_LENGTH, blank=True)

    # condition of the drop
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
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
        unique_together = ("provider", "object")


# ------------------------------------------------------------
#
# quest's rewards
#
# ------------------------------------------------------------
class quest_reward_list(loot_list):
    "Quest's rewards list."

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("provider", "object")


# ------------------------------------------------------------
#
# profit room's rewards
#
# ------------------------------------------------------------
class room_profit_list(loot_list):
    "Profit room's rewards list."

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
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
        app_label = "worlddata"

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

    def __unicode__(self):
        return self.name


# ------------------------------------------------------------
#
# Object's custom properties.
#
# ------------------------------------------------------------
class properties_dict(models.Model):
    """
    Object's custom properties.
    """
    # The key of a element type.
    element_type = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of the property.
    property = models.CharField(max_length=KEY_LENGTH)

    # The name of the property.
    name = models.CharField(max_length=NAME_LENGTH)

    # The description of the property.
    desc = models.TextField(blank=True)

    # Default value.
    default = models.CharField(max_length=VALUE_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("element_type", "property")


# ------------------------------------------------------------
#
# Character's mutable states.
# These states can change in the game.
#
# ------------------------------------------------------------
class character_states_dict(models.Model):
    """
    Character's mutable states.
    """
    # The key of the state.
    key = models.CharField(max_length=KEY_LENGTH, unique=True)

    # The name of the property.
    name = models.CharField(max_length=NAME_LENGTH)

    # Default value.
    default = models.CharField(max_length=VALUE_LENGTH, blank=True)

    # The description of the property.
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


# ------------------------------------------------------------
#
# element's custom properties
#
# ------------------------------------------------------------
class element_properties(models.Model):
    "Store element's custom properties."
    # The type of an element.
    element = models.CharField(max_length=KEY_LENGTH)

    # The key of an element.
    key = models.CharField(max_length=KEY_LENGTH)

    # The level of the element.
    level = models.PositiveIntegerField(blank=True, null=True)

    # The key of the property.
    property = models.CharField(max_length=KEY_LENGTH)

    # The value of the property.
    value = models.CharField(max_length=VALUE_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("element", "key", "level", "property")
        index_together = [("element", "key", "level")]


# ------------------------------------------------------------
#
# character's default objects
#
# ------------------------------------------------------------
class default_objects(models.Model):
    "character's default objects"

    # Character's key.
    character = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The key of an object.
    # Object's key.
    object = models.CharField(max_length=KEY_LENGTH)

    # Object's level.
    level = models.PositiveIntegerField(blank=True, default=0)

    # Object's number
    number = models.PositiveIntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
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

    # The key of a skill.
    # skill's key
    skill = models.CharField(max_length=KEY_LENGTH)

    # skill's level
    level = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("character", "skill")


class quests(models.Model):
    "Store all quests."
    # quest's key
    key = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # quest's name
    name = models.CharField(max_length=NAME_LENGTH, blank=True)

    # quest's description for display
    desc = models.TextField(blank=True)

    # experience that the character get
    exp = models.PositiveIntegerField(blank=True, default=0)

    # the condition to accept this quest.
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    # will do this action after a quest completed
    action = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


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
        unique_together = ("quest", "type", "object")


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
        unique_together = ("quest", "dependency", "type")


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
    trigger_type = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # The type of an event action.
    # event's action
    action = models.CharField(max_length=KEY_LENGTH)

    # The odds of this event.
    odds = models.FloatField(blank=True, default=1.0)

    # Can trigger another event after this one.
    # If multiple is False, no more events will be triggered.
    multiple = models.BooleanField(blank=True, default=True)

    # the condition to enable this event
    condition = models.CharField(max_length=CONDITION_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        index_together = [("trigger_obj", "trigger_type")]

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

    # dialogue's content
    content = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"

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
        unique_together = ("dialogue", "dependency", "type")


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
        unique_together = ("dialogue", "next_dlg")


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
        unique_together = ("npc", "dialogue")


# ------------------------------------------------------------
#
# event's data
#
# ------------------------------------------------------------
class BaseEventActionData(models.Model):
    # The key of an event.
    event_key = models.CharField(max_length=KEY_LENGTH, db_index=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"


# ------------------------------------------------------------
#
# action to attack a target
#
# ------------------------------------------------------------
class action_attack(BaseEventActionData):
    "action attack's data"

    # The key of a common character.
    # mob's key
    mob = models.CharField(max_length=KEY_LENGTH)

    # mob's level
    # Set the level of the mob. If it is 0, use the default level of the mob.
    level = models.IntegerField(blank=True, default=0)

    # event's odds ([0.0, 1.0])
    odds = models.FloatField(blank=True, default=0)

    # combat's description
    desc = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("event_key", "mob", "level")


# ------------------------------------------------------------
#
# action to begin a dialogue
#
# ------------------------------------------------------------
class action_dialogue(BaseEventActionData):
    "Store all event dialogues."

    # The key of a dialogue.
    # dialogue's key
    dialogue = models.CharField(max_length=KEY_LENGTH)

    # The key of an NPC.
    # NPC's key
    npc = models.CharField(max_length=KEY_LENGTH, blank=True)

    # event's odds
    odds = models.FloatField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("event_key", "dialogue", "npc")


# ------------------------------------------------------------
#
# action to learn a skill
#
# ------------------------------------------------------------
class action_learn_skill(BaseEventActionData):
    "Store all actions to learn skills."

    # The key of a skill.
    # skill's key
    skill = models.CharField(max_length=KEY_LENGTH)

    # skill's level
    level = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("event_key", "skill")


# ------------------------------------------------------------
#
# action to accept a quest
#
# ------------------------------------------------------------
class action_accept_quest(BaseEventActionData):
    "Store all actions to accept quests."

    # The key of a quest.
    # quest's key
    quest = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("event_key", "quest")


# ------------------------------------------------------------
#
# action to turn in a quest
#
# ------------------------------------------------------------
class action_turn_in_quest(BaseEventActionData):
    "Store all actions to turn in a quest."

    # The key of a quest.
    # quest's key
    quest = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("event_key", "quest")


# ------------------------------------------------------------
#
# action to close an event
#
# ------------------------------------------------------------
class action_close_event(BaseEventActionData):
    "Store all event closes."

    # The key of an event to close.
    event = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("event_key", "event")


# ------------------------------------------------------------
#
# action to send a message to the character
#
# ------------------------------------------------------------
class action_message(BaseEventActionData):
    """
    The Action to send a message to the character.
    """
    # Messages.
    message = models.CharField(max_length=TEXT_CONTENT_LENGTH, blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("event_key", "message")


# ------------------------------------------------------------
#
# action to trigger other actions at interval.
#
# ------------------------------------------------------------
class action_room_interval(BaseEventActionData):
    """
    The action to trigger other actions at interval.
    """
    # The event action's key.
    action = models.CharField(max_length=KEY_LENGTH)

    # Repeat interval in seconds.
    interval = models.PositiveIntegerField(blank=True, default=0)

    # Can trigger events when the character is offline.
    offline = models.BooleanField(blank=True, default=False)

    # This message will be sent to the character when the interval begins.
    begin_message = models.TextField(blank=True)

    # This message will be sent to the character when the interval ends.
    end_message = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("event_key", "action")


# ------------------------------------------------------------
#
# action to add objects to characters
#
# ------------------------------------------------------------
class action_get_objects(BaseEventActionData):
    """
    The Action to add objects to characters
    """
    # The object's key.
    object = models.CharField(max_length=KEY_LENGTH)

    # The object's number.
    number = models.PositiveIntegerField(blank=True, default=0)

    # The odds to get these objects. ([0.0, 1.0])
    odds = models.FloatField(blank=True, default=0)

    # Can get another object after this one.
    multiple = models.BooleanField(blank=True, default=True)

    # This message will be sent to the character when get objects.
    message = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("event_key", "object")


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
    origin = models.CharField(max_length=TEXT_CONTENT_LENGTH, blank=True)

    # translated worlds
    local = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "worlddata"
        unique_together = ("category", "origin")


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

    def __unicode__(self):
        return self.resource
