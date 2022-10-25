
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
# The base of all data models
#
# ------------------------------------------------------------
class BaseModel(Base):
    """
    The game world system's data.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    def __eq__(self, other):
        """
        Define the equal operator. Two records are equal if they have the same id.
        """
        return int(self.id) == int(other.id)


# ------------------------------------------------------------
#
# The game world system's data.
# Users should not modify it manually.
#
# ------------------------------------------------------------
class system_data(BaseModel):
    """
    The game world system's data.
    """
    __tablename__ = "system_data"

    # The last id of accounts.
    object_index = Column(Integer, default=0, nullable=False)

    test = Column(Integer, default=0, nullable=False)


# ------------------------------------------------------------
#
# Game's basic settings.
#
# ------------------------------------------------------------
class game_settings(BaseModel):
    """
    Game's basic settings.
    NOTE: Only uses the first record!
    """
    __tablename__ = "game_settings"

    # The name of your game.
    game_name = Column(Unicode(NAME_LENGTH))

    # The screen shows to players who are not loggin.
    connection_screen = Column(UnicodeText)

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

    # The key of a world room.
    # The start position for new characters. It is the key of the room.
    # If it is empty, the home will be set to the first room in WORLD_ROOMS.
    start_location_key = Column(String(KEY_LENGTH))

    # The key of a world room.
    # Player's default home. When a player dies, he will be moved to his home.
    default_player_home_key = Column(String(KEY_LENGTH))

    # The key of a character.
    # Default character of players.
    default_player_character_key = Column(String(KEY_LENGTH))

    # The key of a character.
    # Default character of staffs.
    default_staff_character_key = Column(String(KEY_LENGTH))


# ------------------------------------------------------------
#
# Game's basic settings.
#
# ------------------------------------------------------------
class honour_settings(BaseModel):
    """
    honour combat's settings.
    NOTE: Only uses the first record!
    """
    __tablename__ = "honour_settings"

    # The minimum level that a player can attend a honour combat.
    min_honour_level = Column(Integer, default=1, nullable=False)

    # The number of top honour players that a player can see.
    top_rankings_number = Column(Integer, default=10, nullable=False)

    # The number of neighbor players on the honour list that a player can see.
    nearest_rankings_number = Column(Integer, default=10, nullable=False)

    # The number of neighbor players on the honour list that a player can fight.
    # honour_opponents_number = models.PositiveIntegerField(blank=True, default=100)

    # The maximum honour difference that the characters can match. 0 means no limits.
    max_honour_diff = Column(Integer, default=0, nullable=False)

    # The prepare time before starting a match. In seconds.
    preparing_time = Column(Integer, default=10, nullable=False)

    # The minimum time between two matches.
    match_interval = Column(Integer, default=10, nullable=False)


# ------------------------------------------------------------
# Element's basic data.
# ------------------------------------------------------------
class BaseElement(BaseModel):
    """
    The base model of all elements. All elements data are linked with keys.
    """
    __abstract__ = True

    # object's key
    key = Column(String(KEY_LENGTH), unique=True, nullable=False)


class world_channels(BaseElement):
    "The communication channels."
    __tablename__ = "world_channels"

    # channel's element type
    element_type = Column(String(KEY_LENGTH), default="CHANNEL", nullable=False)

    # channel's name
    name = Column(Unicode(NAME_LENGTH))

    # channel's description for display
    desc = Column(UnicodeText)


class BaseMatter(BaseElement):
    """
    Base class for matter tables.
    """
    __abstract__ = True

    # matter's element type
    element_type = Column(String(KEY_LENGTH), nullable=False)

    # matter's name
    name = Column(Unicode(NAME_LENGTH))

    # matter's description for display
    desc = Column(UnicodeText)

    # matter's icon resource
    icon = Column(String(KEY_LENGTH))


# ------------------------------------------------------------
#
# Areas
#
# ------------------------------------------------------------
class world_areas(BaseMatter):
    "The game map is composed by areas."
    __tablename__ = "world_areas"

    __table_args__ = {
        "extend_existing": True,
    }

    # matter's element type
    element_type = Column(String(KEY_LENGTH), nullable=False, default="AREA")

    # area's map background image resource
    background = Column(String(KEY_LENGTH))

    # area's width
    width = Column(Integer, default=0)

    # area's height
    height = Column(Integer, default=0)


# ------------------------------------------------------------
#
# Rooms
#
# ------------------------------------------------------------
class world_rooms(BaseMatter):
    "Defines all unique rooms."
    __tablename__ = "world_rooms"

    __table_args__ = {
        "extend_existing": True,
    }

    # matter's element type
    element_type = Column(String(KEY_LENGTH), nullable=False, default="ROOM")

    # The key of a world area.
    # The room's location, it must be a area.
    area = Column(String(KEY_LENGTH), index=True)

    # players can not fight in peaceful romms
    peaceful = Column(Boolean, default=False)

    # room's position which is used in maps
    position = Column(String(POSITION_LENGTH))

    # room's background image resource
    background = Column(String(KEY_LENGTH))


class profit_rooms(BaseElement):
    """
    The action to trigger other actions at interval.
    """
    __tablename__ = "profit_rooms"

    __table_args__ = {
        "extend_existing": True,
    }

    # matter's element type
    element_type = Column(String(KEY_LENGTH), nullable=False, default="PROFIT_ROOM")

    # Repeat interval in seconds.
    interval = Column(Integer, default=0, nullable=False)

    # Can trigger events when the character is offline.
    offline = Column(Boolean, default=False)

    # This message will be sent to the character when the interval begins.
    begin_message = Column(UnicodeText)

    # This message will be sent to the character when the interval ends.
    end_message = Column(UnicodeText)

    # the condition for getting profits
    condition = Column(String(CONDITION_LENGTH))


# ------------------------------------------------------------
#
# Objects
#
# ------------------------------------------------------------
class common_objects(BaseMatter):
    "Store all common objects."
    __tablename__ = "common_objects"

    __table_args__ = {
        "extend_existing": True,
    }

    # matter's element type
    element_type = Column(String(KEY_LENGTH), nullable=False, default="COMMON_OBJECT")


class world_objects(BaseElement):
    "Store all unique objects."
    __tablename__ = "world_objects"

    # The key of a world room.
    # object's location, it must be a room
    location = Column(String(KEY_LENGTH), index=True)

    # Action's name
    action = Column(String(KEY_LENGTH))


class pocket_objects(BaseElement):
    "Store all pocket objects."
    __tablename__ = "pocket_objects"

    # the max number of this object in one pile, must above 1
    max_stack = Column(Integer, default=1, nullable=False)

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
    skill = Column(String(KEY_LENGTH))

    # skill's level
    level = Column(Integer)


class equipments(BaseElement):
    "equipments inherit from common objects."
    __tablename__ = "equipments"

    # The key of an equipment position.
    # equipment's position
    position = Column(String(KEY_LENGTH), index=True)

    # The key of an equipment type.
    # equipment's type
    type = Column(String(KEY_LENGTH))


class object_creators(BaseElement):
    "Players can get new objects from an object_creator."
    __tablename__ = "object_creators"

    # loot's verb
    loot_verb = Column(Unicode(NAME_LENGTH))

    # loot's condition
    loot_condition = Column(String(CONDITION_LENGTH))


# ------------------------------------------------------------
#
# characters
#
# ------------------------------------------------------------
class characters(BaseMatter):
    "Store common characters."
    __tablename__ = "characters"

    __table_args__ = {
        "extend_existing": True,
    }

    # matter's element type
    element_type = Column(String(KEY_LENGTH), nullable=False, default="CHARACTER")

    # Character's level.
    level = Column(Integer, default=1)

    # Reborn time. The time of reborn after this character was killed. 0 means never reborn.
    reborn_time = Column(Integer, default=0)

    # Default relationship between the character and the player.
    relationship = Column(Integer, default=0)

    # Clone another character's custom properties if this character's data is empty.
    clone = Column(String(KEY_LENGTH))


class world_npcs(BaseElement):
    "Store all NPCs."
    __tablename__ = "world_npcs"

    # NPC's location, it must be a room.
    location = Column(String(KEY_LENGTH), index=True)


class player_characters(BaseElement):
    "Player's character."
    __tablename__ = "player_characters"


# ------------------------------------------------------------
#
# exits connecting between rooms.
#
# ------------------------------------------------------------
class world_exits(BaseMatter):
    "Defines all unique exits."
    __tablename__ = "world_exits"

    __table_args__ = {
        "extend_existing": True,
    }

    # matter's element type
    element_type = Column(String(KEY_LENGTH), nullable=False, default="EXIT")

    # The key of a world room.
    # The exit's location, it must be a room.
    # Players can see and enter an exit from this room.
    location = Column(String(KEY_LENGTH), index=True)

    # The key of a world room.
    # The exits's destination.
    destination = Column(String(KEY_LENGTH))

    # the action verb to enter the exit (optional)
    verb = Column(Unicode(NAME_LENGTH))


class exit_locks(BaseElement):
    "Locked exit's additional data"
    __tablename__ = "exit_locks"

    # condition of the lock
    unlock_condition = Column(String(CONDITION_LENGTH))

    # action to unlock the exit (optional)
    unlock_verb = Column(Unicode(NAME_LENGTH))

    # description when locked
    locked_desc = Column(UnicodeText)

    # description when unlocked
    unlocked_desc = Column(UnicodeText)

    # if the exit can be unlocked automatically
    auto_unlock = Column(Boolean, default=False)

    # when a character unlocked an exit, the exit is unlocked for this character forever.
    unlock_forever = Column(Boolean, default=True)


# ------------------------------------------------------------
#
# Condition desc
#
# ------------------------------------------------------------
class conditional_desc(BaseElement):
    "Matter's conditional descriptions"
    __tablename__ = "conditional_desc"

    __table_args__ = (
        UniqueConstraint("element", "key", "condition"),
    )

    __index_together__ = [("element", "key")]

    # The element's type.
    element = Column(String(KEY_LENGTH), nullable=False)

    # The key of an element.
    key = Column(String(KEY_LENGTH), nullable=False)

    # condition of the description
    condition = Column(String(CONDITION_LENGTH))

    # description
    desc = Column(UnicodeText)


# ------------------------------------------------------------
#
# Skills
#
# ------------------------------------------------------------
class skills(BaseElement):
    "Store all skills."
    __tablename__ = "skills"

    # skill's name
    name = Column(Unicode(NAME_LENGTH))

    # skill's description
    desc = Column(UnicodeText)

    # skill's icon resource
    icon = Column(String(KEY_LENGTH))

    # skill's message when casting
    message = Column(UnicodeText)

    # skill's cd
    cd = Column(Float, default=0)

    # if it is a passive skill
    passive = Column(Boolean, default=False)

    # skill function's name
    function = Column(String(KEY_LENGTH))

    # skill's main type, used in autocasting skills.
    main_type = Column(String(KEY_LENGTH))

    # skill's sub type, used in autocasting skills.
    sub_type = Column(String(KEY_LENGTH))


class shops(BaseElement):
    "Store all shops."
    __tablename__ = "shops"

    # object's element type
    element_type = Column(String(KEY_LENGTH), default="SHOP", nullable=False)

    # shop's name
    name = Column(Unicode(NAME_LENGTH))

    # shop's description
    desc = Column(UnicodeText)

    # the verb to open the shop
    verb = Column(Unicode(NAME_LENGTH))

    # condition of the shop
    condition = Column(String(CONDITION_LENGTH))

    # shop's icon resource
    icon = Column(String(KEY_LENGTH))


class quests(BaseElement):
    "Store all quests."
    __tablename__ = "quests"

    # quest's name
    name = Column(Unicode(NAME_LENGTH))

    # quest's description for display
    desc = Column(UnicodeText)

    # experience that the character get
    exp = Column(Integer, default=0)

    # the condition to accept this quest.
    condition = Column(String(CONDITION_LENGTH))

    # will do this action after a quest completed
    action = Column(String(KEY_LENGTH))


class shop_goods(BaseModel):
    "All goods that sold in shops."
    __tablename__ = "shop_goods"

    # shop's key
    shop = Column(String(KEY_LENGTH), index=True, nullable=False)

    # the key of objects to sell
    goods = Column(String(KEY_LENGTH), index=True, nullable=False)

    # goods level
    level = Column(Integer)

    # number of shop goods
    number = Column(Integer, default=1)

    # the price of the goods
    price = Column(Integer, default=1)

    # the unit of the goods price
    unit = Column(String(KEY_LENGTH), nullable=False)

    # visible condition of the goods
    condition = Column(String(CONDITION_LENGTH))


# ------------------------------------------------------------
#
# store objects loot list
#
# ------------------------------------------------------------
class loot_list(BaseModel):
    "Loot list. It is used in object_creators and mods."
    __abstract__ = True

    __table_args__ = (
        UniqueConstraint("provider", "object"),
    )

    # the provider of the object
    provider = Column(String(KEY_LENGTH), index=True)

    # the key of dropped object
    object = Column(String(KEY_LENGTH), nullable=False)

    # the level of dropped object
    level = Column(Integer)

    # number of dropped object
    number = Column(Integer, default=0)

    # odds of drop, from 0.0 to 1.0
    odds = Column(Float, default=0)

    # Can get another object after this one.
    multiple = Column(Boolean, default=True)

    # This message will be sent to the character when get objects.
    message = Column(UnicodeText)

    # The key of a quest.
    # if it is not empty, the player must have this quest but not accomplish this quest.
    quest = Column(String(KEY_LENGTH))

    # condition of the drop
    condition = Column(String(CONDITION_LENGTH))


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
class equipment_types(BaseModel):
    "Store all equip types."
    __tablename__ = "equipment_types"

    # equipment type's key
    key = Column(String(KEY_LENGTH), unique=True, nullable=False)

    # type's name
    name = Column(Unicode(NAME_LENGTH), unique=True, nullable=False)

    # type's description
    desc = Column(UnicodeText)


# ------------------------------------------------------------
#
# store all available equipment potisions
#
# ------------------------------------------------------------
class equipment_positions(BaseModel):
    "Store all equip types."
    __tablename__ = "equipment_positions"

    # position's key
    key = Column(String(KEY_LENGTH), unique=True, nullable=False)

    # position's name for display
    name = Column(Unicode(NAME_LENGTH), unique=True, nullable=False)

    # position's description
    desc = Column(UnicodeText)


# ------------------------------------------------------------
#
# Object's custom properties.
#
# ------------------------------------------------------------
class properties_dict(BaseModel):
    """
    Object's custom properties.
    """
    __tablename__ = "properties_dict"

    __table_args__ = (
        UniqueConstraint("element_type", "property"),
    )

    # The key of a element type.
    element_type = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of the property.
    property = Column(String(KEY_LENGTH), nullable=False)

    # The name of the property.
    name = Column(Unicode(NAME_LENGTH))

    # The description of the property.
    desc = Column(UnicodeText)

    # Default value.
    default = Column(String(VALUE_LENGTH))


# ------------------------------------------------------------
#
# Character's mutable states.
# These states can change in the game.
#
# ------------------------------------------------------------
class character_states_dict(BaseModel):
    """
    Character's mutable states.
    """
    __tablename__ = "character_states_dict"

    # The key of the state.
    key = Column(String(KEY_LENGTH), unique=True, nullable=False)

    # The name of the property.
    name = Column(Unicode(NAME_LENGTH), unique=True, nullable=False)

    # Default value.
    default = Column(String(VALUE_LENGTH))

    # The description of the property.
    desc = Column(UnicodeText)


# ------------------------------------------------------------
#
# element's custom properties
#
# ------------------------------------------------------------
class element_properties(BaseModel):
    "Store element's custom properties."
    # The type of an element.
    __tablename__ = "element_properties"

    __table_args__ = (
        UniqueConstraint("element", "key", "level", "property"),
    )

    __index_together__ = [("element", "key", "level")]

    # The element's type.
    element = Column(String(KEY_LENGTH), nullable=False)

    # The key of an element.
    key = Column(String(KEY_LENGTH), nullable=False)

    # The level of the element.
    level = Column(Integer)

    # The key of the property.
    property = Column(String(KEY_LENGTH), nullable=False)

    # The value of the property.
    value = Column(String(VALUE_LENGTH))


# ------------------------------------------------------------
#
# character's default objects
#
# ------------------------------------------------------------
class default_objects(BaseModel):
    "character's default objects"
    __tablename__ = "default_objects"

    __table_args__ = (
        UniqueConstraint("character", "object"),
    )

    # Character's key.
    character = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of an object.
    # Object's key.
    object = Column(String(KEY_LENGTH), nullable=False)

    # Object's level.
    level = Column(Integer)

    # Object's number
    number = Column(Integer, default=0)


# ------------------------------------------------------------
#
# store npc's shop
#
# ------------------------------------------------------------
class npc_shops(BaseModel):
    "Store npc's shops."
    __tablename__ = "npc_shops"

    __table_args__ = (
        UniqueConstraint("npc", "shop"),
    )

    # The key of an NPC.
    # NPC's key
    npc = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of a shop.
    # shop's key
    shop = Column(String(KEY_LENGTH), index=True, nullable=False)


# ------------------------------------------------------------
#
# skill types
#
# ------------------------------------------------------------
class skill_types(BaseModel):
    """
    Skill's type, used in skill's main_type and sub_type. The type discribes the usage of a
    skill, which is useful in auto casting skills.
    """
    __tablename__ = "skill_types"

    # type's key
    key = Column(String(KEY_LENGTH), unique=True, nullable=False)

    # the readable name of the skill type
    name = Column(Unicode(NAME_LENGTH), unique=True, nullable=False)

    # skill type's description
    desc = Column(UnicodeText)


# ------------------------------------------------------------
#
# character's default skills
#
# ------------------------------------------------------------
class default_skills(BaseModel):
    "character's default skills"
    __tablename__ = "default_skills"

    __table_args__ = (
        UniqueConstraint("character", "skill"),
    )

    # character's key
    character = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of a skill.
    # skill's key
    skill = Column(String(KEY_LENGTH), nullable=False)

    # skill's level
    level = Column(Integer)


# ------------------------------------------------------------
#
# store quest objectives
#
# ------------------------------------------------------------
class quest_objectives(BaseModel):
    "Store all quest objectives."
    __tablename__ = "quest_objectives"

    __table_args__ = (
        UniqueConstraint("quest", "type", "object"),
    )

    # The key of a quest.
    # quest's key
    quest = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of an objetive type.
    # objective's type
    type = Column(String(KEY_LENGTH), nullable=False)

    # relative object's key
    object = Column(String(KEY_LENGTH))

    # objective's number
    number = Column(Integer, default=0)

    # objective's discription for display
    desc = Column(UnicodeText)


# ------------------------------------------------------------
#
# store quest dependencies
#
# ------------------------------------------------------------
class quest_dependencies(BaseModel):
    "Store quest dependency."
    __tablename__ = "quest_dependencies"

    __table_args__ = (
        UniqueConstraint("quest", "dependency", "type"),
    )

    # The key of a quest.
    # quest's key
    quest = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of a quest.
    # quest that dependends on
    dependency = Column(String(KEY_LENGTH), nullable=False)

    # The key of a quest dependency type.
    # dependency's type
    type = Column(String(KEY_LENGTH), nullable=False)


# ------------------------------------------------------------
#
# store event data
#
# ------------------------------------------------------------
class event_data(BaseModel):
    "Store event data."
    __tablename__ = "event_data"

    __index_together__ =  [("trigger_obj", "trigger_type")]

    # event's key
    key = Column(String(KEY_LENGTH), unique=True, nullable=False)

    # trigger's relative object's key
    trigger_obj = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The type of the event trigger.
    # event's trigger
    trigger_type = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The type of an event action.
    # event's action
    action = Column(String(KEY_LENGTH), nullable=False)

    # The odds of this event.
    odds = Column(Float, default=1.0)

    # Can trigger another event after this one.
    # If multiple is False, no more events will be triggered.
    multiple = Column(Boolean, default=True)

    # the condition to enable this event
    condition = Column(String(CONDITION_LENGTH))


# ------------------------------------------------------------
#
# store all dialogues
#
# ------------------------------------------------------------
class dialogues(BaseModel):
    "Store all dialogues."
    __tablename__ = "dialogues"

    # dialogue's key
    key = Column(String(KEY_LENGTH), unique=True, nullable=False)

    # dialogue's name
    name = Column(Unicode(NAME_LENGTH))

    # condition to show this dialogue
    condition = Column(String(CONDITION_LENGTH))

    # dialogue's content
    content = Column(UnicodeText)


# ------------------------------------------------------------
#
# store dialogue quest dependencies
#
# ------------------------------------------------------------
class dialogue_quest_dependencies(BaseModel):
    "Store dialogue quest dependencies."
    __tablename__ = "dialogue_quest_dependencies"

    __table_args__ = (
        UniqueConstraint("dialogue", "dependency", "type"),
    )

    # The key of a dialogue.
    # dialogue's key
    dialogue = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of a quest.
    # related quest's key
    dependency = Column(String(KEY_LENGTH), nullable=False)

    # The key of a quest dependency type.
    # dependency's type
    type = Column(String(KEY_LENGTH), nullable=False)


# ------------------------------------------------------------
#
# store dialogue relations
#
# ------------------------------------------------------------
class dialogue_relations(BaseModel):
    "Store dialogue relations."
    __tablename__ = "dialogue_relations"

    __table_args__ = (
        UniqueConstraint("dialogue", "next_dlg"),
    )

    # The key of a dialogue.
    # dialogue's key
    dialogue = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of a dialogue.
    # next dialogue's key
    next_dlg = Column(String(KEY_LENGTH), index=True, nullable=False)


# ------------------------------------------------------------
#
# store npc's dialogue
#
# ------------------------------------------------------------
class npc_dialogues(BaseModel):
    "Store npc's dialogues."
    __tablename__ = "npc_dialogues"

    __table_args__ = (
        UniqueConstraint("npc", "dialogue"),
    )

    # The key of an NPC.
    # NPC's key
    npc = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of a dialogue.
    # dialogue's key
    dialogue = Column(String(KEY_LENGTH), index=True, nullable=False)

    # if it is a default dialogue
    default = Column(Boolean, default=False)


# ------------------------------------------------------------
#
# event's data
#
# ------------------------------------------------------------
class BaseEventActionData(BaseModel):
    __abstract__ = True

    # The key of an event.
    event_key = Column(String(KEY_LENGTH), index=True, nullable=False)


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
    )

    # The key of a common character.
    # mob's key
    mob = Column(String(KEY_LENGTH), nullable=False)

    # mob's level
    # Set the level of the mob.
    level = Column(Integer)

    # event's odds ([0.0, 1.0])
    odds = Column(Float, default=0)

    # combat's description
    desc = Column(UnicodeText)


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
    )

    # The key of a dialogue.
    # dialogue's key
    dialogue = Column(String(KEY_LENGTH), nullable=False)

    # The key of an NPC.
    # NPC's key
    npc = Column(String(KEY_LENGTH))

    # event's odds
    odds = Column(Float, default=0)


# ------------------------------------------------------------
#
# action to learn a skill
#
# ------------------------------------------------------------
class action_learn_skill(BaseEventActionData):
    "Store all actions to learn skills."
    __tablename__ = "action_learn_skill"

    __table_args__ = (
        UniqueConstraint("event_key", "skill"),
    )

    # The key of a skill.
    # skill's key
    skill = Column(String(KEY_LENGTH), nullable=False)

    # skill's level
    level = Column(Integer)


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
    )

    # The key of a quest.
    # quest's key
    quest = Column(String(KEY_LENGTH), nullable=False)


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
    )

    # The key of a quest.
    # quest's key
    quest = Column(String(KEY_LENGTH), nullable=False)


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
    )

    # The key of an event to close.
    event = Column(String(KEY_LENGTH), nullable=False)


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
    )

    # Messages.
    message = Column(String(TEXT_CONTENT_LENGTH))


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
    )

    # The object's key.
    object = Column(String(KEY_LENGTH), nullable=False)

    # The object's level.
    level = Column(Integer)

    # The object's number.
    number = Column(Integer, default=0)

    # The odds to get these objects. ([0.0, 1.0])
    odds = Column(Float, default=0)

    # Can get another object after this one.
    multiple = Column(Boolean, default=True)

    # This message will be sent to the character when get objects.
    message = Column(UnicodeText)


# ------------------------------------------------------------
#
# action to set the relationship between a player and an element.
#
# ------------------------------------------------------------
class action_set_relation(BaseEventActionData):
    """
    The Action to send a message to the character.
    """
    __tablename__ = "action_set_relation"

    __table_args__ = (
        UniqueConstraint("element_type", "element_key"),
    )

    # The type of a element type.
    element_type = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of a element type.
    element_key = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The relationship's value
    value = Column(Integer)


# ------------------------------------------------------------
#
# action to add the relationship between a player and an element.
#
# ------------------------------------------------------------
class action_add_relation(BaseEventActionData):
    """
    The Action to send a message to the character.
    """
    __tablename__ = "action_add_relation"

    __table_args__ = (
        UniqueConstraint("element_type", "element_key"),
    )

    # The type of a element type.
    element_type = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The key of a element type.
    element_key = Column(String(KEY_LENGTH), index=True, nullable=False)

    # The relationship's value
    value = Column(Integer)


# ------------------------------------------------------------
#
# localized strings
#
# ------------------------------------------------------------
class localized_strings(BaseModel):
    "Store all localized strings."
    __tablename__ = "localized_strings"

    __table_args__ = (
        UniqueConstraint("category", "origin"),
    )

    # is system data or not
    system_data = Column(Boolean, default=False)

    # word's category
    category = Column(String(KEY_LENGTH), default="", nullable=False)

    # the origin words
    origin = Column(String(TEXT_CONTENT_LENGTH), nullable=False)

    # translated worlds
    local = Column(UnicodeText, nullable=False)


# ------------------------------------------------------------
#
# set image resources
#
# ------------------------------------------------------------
class image_resources(BaseModel):
    "Store resource's information."
    __tablename__ = "image_resources"

    # image's path
    resource = Column(String(KEY_LENGTH), unique=True, nullable=False)

    # image's type
    type = Column(String(KEY_LENGTH), nullable=False)

    # resource'e width
    image_width = Column(Integer, default=0)

    # resource'e height
    image_height = Column(Integer, default=0)
