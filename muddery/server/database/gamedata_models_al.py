
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Time, Boolean, UniqueConstraint
Base = declarative_base()

KEY_LENGTH = 80
NAME_LENGTH = 80
VALUE_LENGTH = 80


class system_data(Base):
    """
    Store system data. Only use the first record.
    """
    __tablename__ = "gamedata_system_data"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The last id of accounts.
    last_account_id = Column(Integer, default=0)

    # The last id of player characters.
    last_player_character_id = Column(Integer, default=0)


# ------------------------------------------------------------
#
# The base of runtime attributes.
#
# ------------------------------------------------------------
class object_states(Base):
    """
    Object's runtime attributes.
    """
    __tablename__ = "gamedata_object_states"

    __table_args__ = (
        UniqueConstraint("obj_id", "key"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # object's id
    obj_id = Column(Integer, index=True)

    # attribute's name
    key = Column(String(KEY_LENGTH), index=True)

    # attribute's value
    value = Column(String(VALUE_LENGTH))


# ------------------------------------------------------------
#
# server bans
#
# ------------------------------------------------------------
class server_bans(Base):
    """
    Banned players.
    """
    __tablename__ = "gamedata_server_bans"

    __table_args__ = (
        UniqueConstraint("type", "target"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ban's type, should be "IP" or "USERNAME"
    type = Column(String(KEY_LENGTH), index=True)

    # IP or name
    target = Column(String(KEY_LENGTH))

    # create time
    create_time = Column(Time)

    # finish time
    finish_time = Column(Time)


# ------------------------------------------------------------
#
# player's accounts
#
# ------------------------------------------------------------
class accounts(Base):
    """
    User accounts.
    """
    __tablename__ = "gamedata_accounts"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # account's username
    username = Column(String(KEY_LENGTH), unique=True)

    # account's password
    password = Column(String(128))

    # account's id
    account_id = Column(Integer, unique=True)

    # account's type
    type = Column(String(KEY_LENGTH), index=True)

    # account's create time
    create_time = Column(Time, nullable=True)

    # account's last login time
    last_login = Column(Time, nullable=True)


# ------------------------------------------------------------
#
# player account's characters
#
# ------------------------------------------------------------
class account_characters(Base):
    "Account's player characters."

    __tablename__ = "gamedata_account_characters"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # player's account id
    account_id = Column(Integer, index=True)

    # playable character's id
    char_id = Column(Integer, unique=True)


# ------------------------------------------------------------
#
# player character's basic information
#
# ------------------------------------------------------------
class character_info(Base):
    "player character's basic information"

    __tablename__ = "gamedata_character_info"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # playable character's id
    char_id = Column(Integer, unique=True)

    # character's nickname
    nickname = Column(String(KEY_LENGTH))

    # character's level
    level = Column(Integer, default=0)


# ------------------------------------------------------------
#
# player character's info
#
# ------------------------------------------------------------
class character_location(Base):
    "player character's location"

    __tablename__ = "gamedata_character_location"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # player character's id
    char_id = Column(Integer, unique=True)

    # location (room's key)
    location = Column(String(KEY_LENGTH))


# ------------------------------------------------------------
#
# player character's inventory
#
# ------------------------------------------------------------
class character_inventory(Base):
    "Player character's inventory."

    __tablename__ = "gamedata_character_inventory"

    __table_args__ = (
        UniqueConstraint("character_id", "position"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id
    character_id = Column(Integer, index=True)

    # position in the inventory
    position = Column(Integer)

    # object's key
    object_key = Column(String(KEY_LENGTH))

    # object's number
    number = Column(Integer, default=0)

    # object's level
    level = Column(Integer, nullable=True)


# ------------------------------------------------------------
#
# player character's equipments
#
# ------------------------------------------------------------
class character_equipments(Base):
    "Player character's equipments."

    __tablename__ = "gamedata_character_equipments"

    __table_args__ = (
        UniqueConstraint("character_id", "position"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id
    character_id = Column(Integer, index=True)

    # the position to put on equipments
    position = Column(String(KEY_LENGTH))

    # object's key
    object_key = Column(String(KEY_LENGTH))

    # object's level
    level = Column(Integer, nullable=True)


# ------------------------------------------------------------
#
# player character's skills
#
# ------------------------------------------------------------
class character_skills(Base):
    "Player character's skills."

    __tablename__ = "gamedata_character_skills"

    __table_args__ = (
        UniqueConstraint("character_id", "skill"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id
    character_id = Column(Integer, index=True)

    # skill's key
    skill = Column(String(KEY_LENGTH))

    # skill's level
    level = Column(Integer, nullable=True)

    # is default skill
    is_default = Column(Boolean, default=False)

    # CD's finish time
    cd_finish = Column(Integer, default=0)


# ------------------------------------------------------------
#
# player character's combat information
#
# ------------------------------------------------------------
class character_combat(Base):
    "Player character's combat."

    __tablename__ = "gamedata_character_combat"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id
    character_id = Column(Integer, unique=True)

    # combat's id
    combat = Column(Integer)


# ------------------------------------------------------------
#
# player character's quests
#
# ------------------------------------------------------------
class character_quests(Base):
    "Player character's quests."

    __tablename__ = "gamedata_character_quests"

    __table_args__ = (
        UniqueConstraint("character_id", "quest"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id
    character_id = Column(Integer, index=True)

    # quest's key
    quest = Column(String(KEY_LENGTH), index=True)

    # quest is finished
    finished = Column(Boolean, default=False, index=True)


# ------------------------------------------------------------
#
# quest objectives
#
# ------------------------------------------------------------
class quest_objectives(Base):
    "Quests' objectives."

    __tablename__ = "gamedata_quest_objectives"

    __table_args__ = (
        UniqueConstraint("character_quest", "objective"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id and quest's key, separated by colon
    character_quest = Column(String(KEY_LENGTH + KEY_LENGTH), index=True)

    # Quest's objective.
    # objective's type and relative object's key, separated by colon
    objective = Column(String(KEY_LENGTH + KEY_LENGTH))

    # objective's progress
    progress = Column(Integer, default=0)


# ------------------------------------------------------------
#
# character's honour
#
# ------------------------------------------------------------
class honours(Base):
    "All character's honours."

    __tablename__ = "gamedata_honours"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's database id
    character = Column(Integer, unique=0)

    # character's honour. special character's honour is -1, such as the superuser.
    honour = Column(Integer, default=-1, index=True)
