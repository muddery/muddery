
import re
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Unicode, Text, UnicodeText, DateTime, Boolean
from sqlalchemy import UniqueConstraint
Base = declarative_base()


KEY_LENGTH = 80
NAME_LENGTH = 80
POSITION_LENGTH = 80
VALUE_LENGTH = 80
CONDITION_LENGTH = 255
TEXT_CONTENT_LENGTH = 255


# ------------------------------------------------------------
#
# The game world system's data.
# Users should not modify it manually.
#
# ------------------------------------------------------------
class system_data(Base):
    """
    The game world system's data.
    """
    __tablename__ = "system_data"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The last id of accounts.
    object_index = Column(Integer, default=0)


# ------------------------------------------------------------
#
# Game's basic settings.
#
# ------------------------------------------------------------
class game_settings(Base):
    """
    Game's basic settings.
    NOTE: Only uses the first record!
    """
    __tablename__ = "game_settings"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The name of your game.
    game_name = Column(Unicode(NAME_LENGTH), default="")

    # The screen shows to players who are not loggin.
    connection_screen = Column(UnicodeText, default="")

    # In solo mode, a player can not see or affect other players.
    solo_mode = Column(Boolean, default=False)

    # Time of global CD.
    global_cd = Column(Float, default=1.0)

    # The CD of auto casting a skill. It must be bigger than GLOBAL_CD
    # They can not be equal!
    auto_cast_skill_cd = Column(Integer, default=1)

    # Allow players to give up quests.
    can_give_up_quests = Column(Boolean, default=True)

    # can close dialogue box or not.
    can_close_dialogue = Column(Boolean, default=False)

    # Can resume unfinished dialogues automatically.
    auto_resume_dialogues = Column(Boolean, default=True)

    # The key of a world room.
    # The start position for new characters. It is the key of the room.
    # If it is empty, the home will be set to the first room in WORLD_ROOMS.
    start_location_key = Column(String(KEY_LENGTH), default="")

    # The key of a world room.
    # Player's default home. When a player dies, he will be moved to his home.
    default_player_home_key = Column(String(KEY_LENGTH), default="")

    # The key of a character.
    # Default character of players.
    default_player_character_key = Column(String(KEY_LENGTH), default="")

    # The key of a character.
    # Default character of staffs.
    default_staff_character_key = Column(String(KEY_LENGTH), default="")


# ------------------------------------------------------------
#
# Game's basic settings.
#
# ------------------------------------------------------------
class honour_settings(Base):
    """
    honour combat's settings.
    NOTE: Only uses the first record!
    """
    __tablename__ = "honour_settings"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The minimum level that a player can attend a honour combat.
    min_honour_level = Column(Integer, default=1)

    # The number of top honour players that a player can see.
    top_rankings_number = Column(Integer, default=10)

    # The number of neighbor players on the honour list that a player can see.
    nearest_rankings_number = Column(Integer, default=10)

    # The number of neighbor players on the honour list that a player can fight.
    # honour_opponents_number = models.PositiveIntegerField(blank=True, default=100)

    # The maximum honour difference that the characters can match. 0 means no limits.
    max_honour_diff = Column(Integer, default=0)

    # The prepare time before starting a match. In seconds.
    preparing_time = Column(Integer, default=10)

    # The minimum time between two matches.
    match_interval = Column(Integer, default=10)


# ------------------------------------------------------------
# Element's basic data.
# ------------------------------------------------------------
class BaseElement(Base):
    """
    The base model of all elements. All elements data are linked with keys.
    """
    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # object's key
    key = Column(String(KEY_LENGTH), unique=True)


class world_channels(BaseElement):
    "The communication channels."
    __tablename__ = "world_channels"

    # channel's element type
    element_type = Column(String(KEY_LENGTH), default="CHANNEL")

    # channel's name
    name = Column(Unicode(NAME_LENGTH), default="")

    # channel's description for display
    desc = Column(UnicodeText, default="")


class world_areas(BaseElement):
    "The game map is composed by areas."
    __tablename__ = "world_areas"

    # area's element type
    element_type = Column(String(KEY_LENGTH), default="AREA")

    # area's name
    name = Column(Unicode(NAME_LENGTH), default="")

    # area's description for display
    desc = Column(UnicodeText, default="")

    # area's icon resource
    icon = Column(String(KEY_LENGTH), default="")

    # area's map background image resource
    background = Column(String(KEY_LENGTH), default="")

    # area's width
    width = Column(Integer, default=0)

    # area's height
    height = Column(Integer, default=0)


class world_rooms(BaseElement):
    "Defines all unique rooms."
    __tablename__ = "world_rooms"

    # room's element type
    element_type = Column(String(KEY_LENGTH), default="ROOM")

    # room's name
    name = Column(Unicode(NAME_LENGTH), default="")

    # room's description for display
    desc = Column(UnicodeText, default="")

    # room's icon resource
    icon = Column(String(KEY_LENGTH), default="")

    # The key of a world area.
    # The room's location, it must be a area.
    area = Column(String(KEY_LENGTH), default="", index=True)

    # players can not fight in peaceful romms
    peaceful = Column(Boolean, default=False)

    # room's position which is used in maps
    position = Column(String(POSITION_LENGTH), default="")

    # room's background image resource
    background = Column(String(KEY_LENGTH), default="")


# ------------------------------------------------------------
#
# rooms that can give profits to characters in the room.
#
# ------------------------------------------------------------
class profit_rooms(BaseElement):
    """
    The action to trigger other actions at interval.
    """
    __tablename__ = "profit_rooms"

    # Repeat interval in seconds.
    interval = Column(Integer, default=0)

    # Can trigger events when the character is offline.
    offline = Column(Boolean, default=False)

    # This message will be sent to the character when the interval begins.
    begin_message = Column(UnicodeText, default="")

    # This message will be sent to the character when the interval ends.
    end_message = Column(UnicodeText, default="")

    # the condition for getting profits
    condition = Column(String(CONDITION_LENGTH), default="")


class world_objects(BaseElement):
    "Store all unique objects."
    __tablename__ = "world_objects"

    # The key of a world room.
    # object's location, it must be a room
    location = Column(String(KEY_LENGTH), default="")

    # Action's name
    action = Column(String(KEY_LENGTH), default="")

    # the condition for showing the object
    condition = Column(String(CONDITION_LENGTH), default="")

    # object's icon resource
    icon = Column(String(KEY_LENGTH), default="")


class common_objects(BaseElement):
    "Store all common objects."
    __tablename__ = "common_objects"

    # object's element type
    element_type = Column(String(KEY_LENGTH), default="COMMON_OBJECT")

    # object's name
    name = Column(Unicode(NAME_LENGTH), default="")

    # object's description for display
    desc = Column(UnicodeText, default="")

    # object's icon resource
    icon = Column(String(KEY_LENGTH), default="")


class pocket_objects(BaseElement):
    "Store all pocket objects."
    __tablename__ = "pocket_objects"

    # the max number of this object in one pile, must above 1
    max_stack = Column(Integer, default=1)

    # if can have only one pile of this object
    unique = Column(Boolean, default=False)

    # if this object can be removed from the inventory when its number is decreased to zero.
    can_remove = Column(Boolean, default=True)

    # if this object can discard
    can_discard = Column(Boolean, default=True)


class foods(BaseElement):
    "Foods inherit from common objects."
    __tablename__ = "foods"


class skill_books(BaseElement):
    "Skill books inherit from common objects."
    __tablename__ = "skill_books"

    # skill's key
    skill = Column(String(KEY_LENGTH), default="")

    # skill's level
    level = Column(Integer, nullable=True)


class equipments(BaseElement):
    "equipments inherit from common objects."
    __tablename__ = "equipments"

    # The key of an equipment position.
    # equipment's position
    position = Column(String(KEY_LENGTH), default="", index=True)

    # The key of an equipment type.
    # equipment's type
    type = Column(String(KEY_LENGTH), default="")


class characters(BaseElement):
    "Store common characters."
    __tablename__ = "characters"

    # object's element type
    element_type = Column(String(KEY_LENGTH), default="CHARACTER")

    # object's name
    name = Column(Unicode(NAME_LENGTH), default="")

    # object's description for display
    desc = Column(UnicodeText, default="")

    # object's icon resource
    icon = Column(String(KEY_LENGTH), default="")

    # Character's level.
    level = Column(Integer, default=1)

    # Reborn time. The time of reborn after this character was killed. 0 means never reborn.
    reborn_time = Column(Integer, default=0)

    # Friendly of this character.
    friendly = Column(Integer, default=0)

    # Clone another character's custom properties if this character's data is empty.
    clone = Column(String(KEY_LENGTH), default="")


class world_npcs(BaseElement):
    "Store all NPCs."
    __tablename__ = "world_npcs"

    # NPC's location, it must be a room.
    location = Column(String(KEY_LENGTH), default="", index=True)

    # the condition for showing the NPC
    condition = Column(String(CONDITION_LENGTH), default="")


class player_characters(BaseElement):
    "Player's character."
    __tablename__ = "player_characters"


class staff_characters(BaseElement):
    "Staff's character."
    __tablename__ = "staff_characters"


# ------------------------------------------------------------
#
# exits connecting between rooms.
#
# ------------------------------------------------------------
class world_exits(BaseElement):
    "Defines all unique exits."
    __tablename__ = "world_exits"

    # object's element type
    element_type = Column(String(KEY_LENGTH), default="EXIT")

    # The exit's name.
    name = Column(Unicode(NAME_LENGTH), default="")

    # The key of a world room.
    # The exit's location, it must be a room.
    # Players can see and enter an exit from this room.
    location = Column(String(KEY_LENGTH), default="", index=True)

    # The key of a world room.
    # The exits's destination.
    destination = Column(String(KEY_LENGTH), default="")

    # the action verb to enter the exit (optional)
    verb = Column(Unicode(NAME_LENGTH), default="")

    # the condition to show the exit
    condition = Column(String(CONDITION_LENGTH), default="")


# ------------------------------------------------------------
#
# exit lock's additional data
#
# ------------------------------------------------------------
class exit_locks(BaseElement):
    "Locked exit's additional data"
    __tablename__ = "exit_locks"

    # condition of the lock
    unlock_condition = Column(String(CONDITION_LENGTH), default="")

    # action to unlock the exit (optional)
    unlock_verb = Column(Unicode(NAME_LENGTH), default="")

    # description when locked
    locked_desc = Column(UnicodeText, default="")

    # description when unlocked
    unlocked_desc = Column(UnicodeText, default="")

    # if the exit can be unlocked automatically
    auto_unlock = Column(Boolean, default=False)

    # when a character unlocked an exit, the exit is unlocked for this character forever.
    unlock_forever = Column(Boolean, default=True)


# ------------------------------------------------------------
#
# object creator's additional data
#
# ------------------------------------------------------------
class object_creators(BaseElement):
    "Players can get new objects from an object_creator."
    __tablename__ = "object_creators"

    # loot's verb
    loot_verb = Column(Unicode(NAME_LENGTH), default="")

    # loot's condition
    loot_condition = Column(String(CONDITION_LENGTH), default="")


class skills(BaseElement):
    "Store all skills."
    __tablename__ = "skills"

    # skill's name
    name = Column(Unicode(NAME_LENGTH), default="")

    # skill's description
    desc = Column(UnicodeText, default="")

    # skill's message when casting
    message = Column(UnicodeText, default="")

    # skill's cd
    cd = Column(Float, default=0)

    # if it is a passive skill
    passive = Column(Boolean, default=False)

    # skill function's name
    function = Column(String(KEY_LENGTH), default="")

    # skill's icon resource
    icon = Column(String(KEY_LENGTH), default="")

    # skill's main type, used in autocasting skills.
    main_type = Column(String(KEY_LENGTH), default="")

    # skill's sub type, used in autocasting skills.
    sub_type = Column(String(KEY_LENGTH), default="")


class shops(BaseElement):
    "Store all shops."
    __tablename__ = "skills"

    # object's element type
    element_type = Column(String(KEY_LENGTH), default="SHOP")

    # shop's name
    name = Column(Unicode(NAME_LENGTH), default="")

    # shop's description
    desc = Column(UnicodeText, default="")

    # the verb to open the shop
    verb = Column(Unicode(NAME_LENGTH), default="")

    # condition of the shop
    condition = Column(String(CONDITION_LENGTH), default="")

    # shop's icon resource
    icon = Column(String(KEY_LENGTH), default="")


class quests(BaseElement):
    "Store all quests."
    __tablename__ = "quests"

    # quest's name
    name = Column(Unicode(NAME_LENGTH), default="")

    # quest's description for display
    desc = Column(UnicodeText, default="")

    # experience that the character get
    exp = Column(Integer, default=0)

    # the condition to accept this quest.
    condition = Column(String(CONDITION_LENGTH), default="")

    # will do this action after a quest completed
    action = Column(String(KEY_LENGTH), default="")


class shop_goods(Base):
    "All goods that sold in shops."
    __tablename__ = "shop_goods"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # shop's key
    shop = Column(String(KEY_LENGTH), index=True)

    # the key of objects to sell
    goods = Column(String(KEY_LENGTH), index=True)

    # goods level
    level = Column(Integer, nullable=True)

    # number of shop goods
    number = Column(Integer, default=1)

    # the price of the goods
    price = Column(Integer, default=1)

    # the unit of the goods price
    unit = Column(String(KEY_LENGTH))

    # visible condition of the goods
    condition = Column(String(CONDITION_LENGTH), default="")


# ------------------------------------------------------------
#
# store objects loot list
#
# ------------------------------------------------------------
class loot_list(Base):
    "Loot list. It is used in object_creators and mods."
    __table_args__ = (
        UniqueConstraint("provider", "object"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # the provider of the object
    provider = Column(String(KEY_LENGTH), index=True)

    # the key of dropped object
    object = Column(String(KEY_LENGTH))

    # the level of dropped object
    level = Column(Integer, nullable=True)

    # number of dropped object
    number = Column(Integer, default=0)

    # odds of drop, from 0.0 to 1.0
    odds = Column(Float, default=0)

    # Can get another object after this one.
    multiple = Column(Boolean, default=True)

    # This message will be sent to the character when get objects.
    message = Column(UnicodeText, default="")

    # The key of a quest.
    # if it is not empty, the player must have this quest but not accomplish this quest.
    quest = Column(String(KEY_LENGTH), default="")

    # condition of the drop
    condition = Column(String(CONDITION_LENGTH), default="")


# ------------------------------------------------------------
#
# object creator's loot list
#
# ------------------------------------------------------------
class creator_loot_list(loot_list):
    "Store character's loot list."
    __tablename__ = "creator_loot_list"


# ------------------------------------------------------------
#
# character's loot list
#
# ------------------------------------------------------------
class character_loot_list(loot_list):
    "Store character's loot list."
    __tablename__ = "character_loot_list"


# ------------------------------------------------------------
#
# quest's rewards
#
# ------------------------------------------------------------
class quest_reward_list(loot_list):
    "Quest's rewards list."
    __tablename__ = "quest_reward_list"


# ------------------------------------------------------------
#
# profit room's rewards
#
# ------------------------------------------------------------
class room_profit_list(loot_list):
    "Profit room's rewards list."
    __tablename__ = "room_profit_list"


# ------------------------------------------------------------
#
# store all equip_types
#
# ------------------------------------------------------------
class equipment_types(Base):
    "Store all equip types."
    __tablename__ = "equipment_types"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # equipment type's key
    key = Column(String(KEY_LENGTH), unique=True)

    # type's name
    name = Column(Unicode(NAME_LENGTH), unique=True)

    # type's description
    desc = Column(UnicodeText, default="")


# ------------------------------------------------------------
#
# store all available equipment potisions
#
# ------------------------------------------------------------
class equipment_positions(Base):
    "Store all equip types."
    __tablename__ = "equipment_positions"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # position's key
    key = Column(String(KEY_LENGTH), unique=True)

    # position's name for display
    name = Column(Unicode(NAME_LENGTH), unique=True)

    # position's description
    desc = Column(UnicodeText, default="")


# ------------------------------------------------------------
#
# Object's custom properties.
#
# ------------------------------------------------------------
class properties_dict(Base):
    """
    Object's custom properties.
    """
    __tablename__ = "properties_dict"

    __table_args__ = (
        UniqueConstraint("element_type", "property"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The key of a element type.
    element_type = Column(String(KEY_LENGTH), index=True)

    # The key of the property.
    property = Column(String(KEY_LENGTH))

    # The name of the property.
    name = Column(Unicode(NAME_LENGTH), unique=True)

    # The description of the property.
    desc = Column(UnicodeText, default="")

    # Default value.
    default = Column(String(VALUE_LENGTH), default="")


# ------------------------------------------------------------
#
# Character's mutable states.
# These states can change in the game.
#
# ------------------------------------------------------------
class character_states_dict(Base):
    """
    Character's mutable states.
    """
    __tablename__ = "character_states_dict"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The key of the state.
    key = Column(String(KEY_LENGTH), unique=True)

    # The name of the property.
    name = Column(Unicode(NAME_LENGTH), unique=True)

    # Default value.
    default = Column(String(VALUE_LENGTH), default="")

    # The description of the property.
    desc = Column(UnicodeText, default="")


# ------------------------------------------------------------
#
# element's custom properties
#
# ------------------------------------------------------------
class element_properties(Base):
    "Store element's custom properties."
    # The type of an element.
    __tablename__ = "properties_dict"

    __table_args__ = (
        UniqueConstraint("element", "key", "level", "property"),
        {
            "extend_existing": True,
            "index_together": [("element", "key", "level")],
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The element's type.
    element = Column(String(KEY_LENGTH), index=True)

    # The key of an element.
    key = Column(String(KEY_LENGTH), index=True)

    # The level of the element.
    level = Column(Integer, nullable=True, index=True)

    # The key of the property.
    property = Column(String(KEY_LENGTH), index=True)

    # The value of the property.
    value = Column(String(VALUE_LENGTH), default="")


# ------------------------------------------------------------
#
# character's default objects
#
# ------------------------------------------------------------
class default_objects(Base):
    "character's default objects"
    __tablename__ = "default_objects"

    __table_args__ = (
        UniqueConstraint("character", "object"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Character's key.
    character = Column(String(KEY_LENGTH), index=True)

    # The key of an object.
    # Object's key.
    object = Column(String(KEY_LENGTH))

    # Object's level.
    level = Column(Integer, nullable=True, index=True)

    # Object's number
    number = Column(Integer, default=0)


# ------------------------------------------------------------
#
# store npc's shop
#
# ------------------------------------------------------------
class npc_shops(Base):
    "Store npc's shops."
    __tablename__ = "npc_shops"

    __table_args__ = (
        UniqueConstraint("npc", "shop"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The key of an NPC.
    # NPC's key
    npc = Column(String(KEY_LENGTH), index=True)

    # The key of a shop.
    # shop's key
    shop = Column(String(KEY_LENGTH), index=True)


# ------------------------------------------------------------
#
# skill types
#
# ------------------------------------------------------------
class skill_types(Base):
    """
    Skill's type, used in skill's main_type and sub_type. The type discribes the usage of a
    skill, which is useful in auto casting skills.
    """
    __tablename__ = "skill_types"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # type's key
    key = Column(String(KEY_LENGTH), unique=True)

    # the readable name of the skill type
    name = Column(Unicode(NAME_LENGTH), unique=True)

    # skill type's description
    desc = Column(UnicodeText, default="")


# ------------------------------------------------------------
#
# character's default skills
#
# ------------------------------------------------------------
class default_skills(Base):
    "character's default skills"
    __tablename__ = "default_skills"

    __table_args__ = (
        UniqueConstraint("character", "skill"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's key
    character = Column(String(KEY_LENGTH), index=True)

    # The key of a skill.
    # skill's key
    skill = Column(String(KEY_LENGTH))

    # skill's level
    level = Column(Integer, nullable=True)


# ------------------------------------------------------------
#
# store quest objectives
#
# ------------------------------------------------------------
class quest_objectives(Base):
    "Store all quest objectives."
    __tablename__ = "quest_objectives"

    __table_args__ = (
        UniqueConstraint("quest", "type", "object"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The key of a quest.
    # quest's key
    quest = Column(String(KEY_LENGTH), index=True)

    # The key of an objetive type.
    # objective's type
    type = Column(String(KEY_LENGTH))

    # relative object's key
    object = Column(String(KEY_LENGTH), default="")

    # objective's number
    number = Column(Integer, default=0)

    # objective's discription for display
    desc = Column(UnicodeText, default="")


# ------------------------------------------------------------
#
# store quest dependencies
#
# ------------------------------------------------------------
class quest_dependencies(Base):
    "Store quest dependency."
    __tablename__ = "quest_dependencies"

    __table_args__ = (
        UniqueConstraint("quest", "dependency", "type"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The key of a quest.
    # quest's key
    quest = Column(String(KEY_LENGTH), index=True)

    # The key of a quest.
    # quest that dependends on
    dependency = Column(String(KEY_LENGTH))

    # The key of a quest dependency type.
    # dependency's type
    type = Column(String(KEY_LENGTH))


# ------------------------------------------------------------
#
# store event data
#
# ------------------------------------------------------------
class event_data(Base):
    "Store event data."
    __tablename__ = "event_data"

    __table_args__ = {
        "extend_existing": True,
        "index-together": [("trigger_obj", "trigger_type")],
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # event's key
    key = Column(String(KEY_LENGTH), unique=True)

    # trigger's relative object's key
    trigger_obj = Column(String(KEY_LENGTH), index=True)

    # The type of the event trigger.
    # event's trigger
    trigger_type = Column(String(KEY_LENGTH), index=True)

    # The type of an event action.
    # event's action
    action = Column(String(KEY_LENGTH))

    # The odds of this event.
    odds = Column(Float, default=1.0)

    # Can trigger another event after this one.
    # If multiple is False, no more events will be triggered.
    multiple = Column(Boolean, default=True)

    # the condition to enable this event
    condition = Column(String(CONDITION_LENGTH), default="")


# ------------------------------------------------------------
#
# store all dialogues
#
# ------------------------------------------------------------
class dialogues(Base):
    "Store all dialogues."
    __tablename__ = "dialogues"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # dialogue's key
    key = Column(String(KEY_LENGTH), unique=True)

    # dialogue's name
    name = Column(Unicode(NAME_LENGTH), unique=True)

    # condition to show this dialogue
    condition = Column(String(CONDITION_LENGTH), default="")

    # dialogue's content
    content = Column(UnicodeText, default="")


# ------------------------------------------------------------
#
# store dialogue quest dependencies
#
# ------------------------------------------------------------
class dialogue_quest_dependencies(Base):
    "Store dialogue quest dependencies."
    __tablename__ = "dialogue_quest_dependencies"

    __table_args__ = (
        UniqueConstraint("dialogue", "dependency", "type"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The key of a dialogue.
    # dialogue's key
    dialogue = Column(String(KEY_LENGTH), index=True)

    # The key of a quest.
    # related quest's key
    dependency = Column(String(KEY_LENGTH))

    # The key of a quest dependency type.
    # dependency's type
    type = Column(String(KEY_LENGTH))


# ------------------------------------------------------------
#
# store dialogue relations
#
# ------------------------------------------------------------
class dialogue_relations(Base):
    "Store dialogue relations."
    __tablename__ = "dialogue_relations"

    __table_args__ = (
        UniqueConstraint("dialogue", "next_dlg"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The key of a dialogue.
    # dialogue's key
    dialogue = Column(String(KEY_LENGTH), index=True)

    # The key of a dialogue.
    # next dialogue's key
    next_dlg = Column(String(KEY_LENGTH), index=True)


# ------------------------------------------------------------
#
# store npc's dialogue
#
# ------------------------------------------------------------
class npc_dialogues(Base):
    "Store npc's dialogues."
    __tablename__ = "dialogue_relations"

    __table_args__ = (
        UniqueConstraint("npc", "dialogue"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The key of an NPC.
    # NPC's key
    npc = Column(String(KEY_LENGTH), index=True)

    # The key of a dialogue.
    # dialogue's key
    dialogue = Column(String(KEY_LENGTH), index=True)

    # if it is a default dialogue
    default = Column(Boolean, default=False)


# ------------------------------------------------------------
#
# event's data
#
# ------------------------------------------------------------
class BaseEventActionData(Base):
    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The key of an event.
    event_key = Column(String(KEY_LENGTH), index=True)


# ------------------------------------------------------------
#
# action to attack a target
#
# ------------------------------------------------------------
class action_attack(BaseEventActionData):
    "action attack's data"
    __tablename__ = "action_attack"

    __table_args__ = (
        UniqueConstraint("event_key", "mob", "level"),
        {
            "extend_existing": True,
        }
    )

    # The key of a common character.
    # mob's key
    mob = Column(String(KEY_LENGTH))

    # mob's level
    # Set the level of the mob.
    level = Column(Integer, nullable=True)

    # event's odds ([0.0, 1.0])
    odds = Column(Float, default=0)

    # combat's description
    desc = Column(UnicodeText, default="")


# ------------------------------------------------------------
#
# action to begin a dialogue
#
# ------------------------------------------------------------
class action_dialogue(BaseEventActionData):
    "Store all event dialogues."
    __tablename__ = "action_dialogue"

    __table_args__ = (
        UniqueConstraint("event_key", "dialogue", "npc"),
        {
            "extend_existing": True,
        }
    )

    # The key of a dialogue.
    # dialogue's key
    dialogue = Column(String(KEY_LENGTH))

    # The key of an NPC.
    # NPC's key
    npc = Column(String(KEY_LENGTH), default="")

    # event's odds
    odds = Column(Float, default=0)


# ------------------------------------------------------------
#
# action to learn a skill
#
# ------------------------------------------------------------
class action_learn_skill(BaseEventActionData):
    "Store all actions to learn skills."
    __tablename__ = "action_dialogue"

    __table_args__ = (
        UniqueConstraint("event_key", "skill"),
        {
            "extend_existing": True,
        }
    )

    # The key of a skill.
    # skill's key
    skill = Column(String(KEY_LENGTH))

    # skill's level
    level = Column(Integer, nullable=True)


# ------------------------------------------------------------
#
# action to accept a quest
#
# ------------------------------------------------------------
class action_accept_quest(BaseEventActionData):
    "Store all actions to accept quests."
    __tablename__ = "action_accept_quest"

    __table_args__ = (
        UniqueConstraint("event_key", "quest"),
        {
            "extend_existing": True,
        }
    )

    # The key of a quest.
    # quest's key
    quest = Column(String(KEY_LENGTH))


# ------------------------------------------------------------
#
# action to turn in a quest
#
# ------------------------------------------------------------
class action_turn_in_quest(BaseEventActionData):
    "Store all actions to turn in a quest."
    __tablename__ = "action_turn_in_quest"

    __table_args__ = (
        UniqueConstraint("event_key", "quest"),
        {
            "extend_existing": True,
        }
    )

    # The key of a quest.
    # quest's key
    quest = Column(String(KEY_LENGTH))


# ------------------------------------------------------------
#
# action to close an event
#
# ------------------------------------------------------------
class action_close_event(BaseEventActionData):
    "Store all event closes."
    __tablename__ = "action_close_event"

    __table_args__ = (
        UniqueConstraint("event_key", "event"),
        {
            "extend_existing": True,
        }
    )

    # The key of an event to close.
    event = Column(String(KEY_LENGTH))


# ------------------------------------------------------------
#
# action to send a message to the character
#
# ------------------------------------------------------------
class action_message(BaseEventActionData):
    """
    The Action to send a message to the character.
    """
    __tablename__ = "action_message"

    __table_args__ = (
        UniqueConstraint("event_key", "message"),
        {
            "extend_existing": True,
        }
    )

    # Messages.
    message = Column(String(TEXT_CONTENT_LENGTH), default="")


# ------------------------------------------------------------
#
# action to add objects to characters
#
# ------------------------------------------------------------
class action_get_objects(BaseEventActionData):
    """
    The Action to add objects to characters
    """
    __tablename__ = "action_get_objects"

    __table_args__ = (
        UniqueConstraint("event_key", "object"),
        {
            "extend_existing": True,
        }
    )

    # The object's key.
    object = Column(String(KEY_LENGTH))

    # The object's level.
    level = Column(Integer, nullable=True)

    # The object's number.
    number = Column(Integer, default=0)

    # The odds to get these objects. ([0.0, 1.0])
    odds = Column(Float, default=0)

    # Can get another object after this one.
    multiple = Column(Boolean, default=True)

    # This message will be sent to the character when get objects.
    message = Column(UnicodeText, default="")


# ------------------------------------------------------------
#
# localized strings
#
# ------------------------------------------------------------
class localized_strings(Base):
    "Store all localized strings."
    __tablename__ = "localized_strings"

    __table_args__ = (
        UniqueConstraint("category", "origin"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # is system data or not
    system_data = Column(Boolean, default=False)

    # word's category
    category = Column(String(KEY_LENGTH), default="")

    # the origin words
    origin = Column(String(TEXT_CONTENT_LENGTH))

    # translated worlds
    local = Column(UnicodeText)


# ------------------------------------------------------------
#
# set image resources
#
# ------------------------------------------------------------
class image_resources(Base):
    "Store resource's information."
    __tablename__ = "image_resources"

    __table_args__ = {
            "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # image's path
    resource = Column(String(KEY_LENGTH), unique=True)

    # image's type
    type = Column(String(KEY_LENGTH))

    # resource'e width
    image_width = Column(Integer, default=0)

    # resource'e height
    image_height = Column(Integer, default=0)
