
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy import UniqueConstraint
Base = declarative_base()

KEY_LENGTH = 80
NAME_LENGTH = 80
VALUE_LENGTH = 80


class system_data(Base):
    """
    Store system data. Only use the first record.
    """
    __tablename__ = "system_data"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # The last id of accounts.
    last_account_id = Column(Integer, default=0, nullable=False)

    # The last id of player characters.
    last_player_character_id = Column(Integer, default=0, nullable=False)


# ------------------------------------------------------------
#
# The base of runtime attributes.
#
# ------------------------------------------------------------
class object_states(Base):
    """
    Object's runtime attributes.
    """
    __tablename__ = "object_states"

    __table_args__ = (
        UniqueConstraint("obj_id", "key"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # object's id
    obj_id = Column(Integer, index=True, nullable=False)

    # attribute's name
    key = Column(String(KEY_LENGTH), index=True, nullable=False)

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
    __tablename__ = "server_bans"

    __table_args__ = (
        UniqueConstraint("type", "target"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ban's type, should be "IP" or "USERNAME"
    type = Column(String(KEY_LENGTH), index=True, nullable=False)

    # IP or name
    target = Column(String(KEY_LENGTH), nullable=False)

    # create time
    create_time = Column(DateTime)

    # finish time
    finish_time = Column(DateTime)


# ------------------------------------------------------------
#
# player's accounts
#
# ------------------------------------------------------------
class accounts(Base):
    """
    User accounts.
    """
    __tablename__ = "accounts"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # account's username
    username = Column(String(KEY_LENGTH), unique=True, nullable=False)

    # account's password
    password = Column(String(128), nullable=False)

    # password's salt
    salt = Column(String(128), nullable=False)

    # account's id
    account_id = Column(Integer, unique=True, nullable=False)

    # account's type
    type = Column(String(KEY_LENGTH), index=True, nullable=False)

    # account's create time
    create_time = Column(DateTime, nullable=True)

    # account's last login time
    last_login = Column(DateTime, nullable=True)


# ------------------------------------------------------------
#
# player account's characters
#
# ------------------------------------------------------------
class account_characters(Base):
    "Account's player characters."

    __tablename__ = "account_characters"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # player's account id
    account_id = Column(Integer, index=True, nullable=False)

    # playable character's id
    char_id = Column(Integer, unique=True, nullable=False)

# ------------------------------------------------------------
#
# player character's basic information
#
# ------------------------------------------------------------
class character_info(Base):
    "player character's basic information"

    __tablename__ = "character_info"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # playable character's id
    char_id = Column(Integer, unique=True, nullable=False)

    # character's element type
    element_type = Column(String(KEY_LENGTH), nullable=False)

    # character's key
    element_key = Column(String(KEY_LENGTH), nullable=False)

    # character's nickname
    nickname = Column(String(KEY_LENGTH), nullable=False)

    # character's level
    level = Column(Integer, default=0)


# ------------------------------------------------------------
#
# player character's info
#
# ------------------------------------------------------------
class character_location(Base):
    "player character's location"

    __tablename__ = "character_location"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # player character's id
    char_id = Column(Integer, unique=True, nullable=False)

    # location (room's key)
    location = Column(String(KEY_LENGTH))


# ------------------------------------------------------------
#
# player character's inventory
#
# ------------------------------------------------------------
class character_inventory(Base):
    "Player character's inventory."

    __tablename__ = "character_inventory"

    __table_args__ = (
        UniqueConstraint("character_id", "position"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id
    character_id = Column(Integer, index=True, nullable=False)

    # position in the inventory
    position = Column(Integer, nullable=False)

    # object's key
    object_key = Column(String(KEY_LENGTH), nullable=False)

    # object's number
    number = Column(Integer, default=0)

    # object's level
    level = Column(Integer)


# ------------------------------------------------------------
#
# player character's equipments
#
# ------------------------------------------------------------
class character_equipments(Base):
    "Player character's equipments."

    __tablename__ = "character_equipments"

    __table_args__ = (
        UniqueConstraint("character_id", "position"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id
    character_id = Column(Integer, index=True, nullable=False)

    # the position to put on equipments
    position = Column(String(KEY_LENGTH), nullable=False)

    # object's key
    object_key = Column(String(KEY_LENGTH), nullable=False)

    # object's level
    level = Column(Integer)


# ------------------------------------------------------------
#
# player character's skills
#
# ------------------------------------------------------------
class character_skills(Base):
    "Player character's skills."

    __tablename__ = "character_skills"

    __table_args__ = (
        UniqueConstraint("character_id", "skill"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id
    character_id = Column(Integer, index=True, nullable=False)

    # skill's key
    skill = Column(String(KEY_LENGTH), nullable=False)

    # skill's level
    level = Column(Integer)

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

    __tablename__ = "character_combat"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id
    character_id = Column(Integer, unique=True, nullable=False)

    # combat's id
    combat = Column(Integer, nullable=False)


# ------------------------------------------------------------
#
# player character's quests
#
# ------------------------------------------------------------
class character_quests(Base):
    "Player character's quests."

    __tablename__ = "character_quests"

    __table_args__ = (
        UniqueConstraint("character_id", "quest"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id
    character_id = Column(Integer, index=True, nullable=False)

    # quest's key
    quest = Column(String(KEY_LENGTH), index=True, nullable=False)

    # quest is finished
    finished = Column(Boolean, default=False, index=True, nullable=False)


# ------------------------------------------------------------
#
# Player character's quest objectives.
#
# ------------------------------------------------------------
class character_quest_objectives(Base):
    "Quests' objectives."

    __tablename__ = "character_quest_objectives"

    __table_args__ = (
        UniqueConstraint("character_quest", "objective"),
        {
            "extend_existing": True,
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's id and quest's key, separated by colon
    character_quest = Column(String(KEY_LENGTH + KEY_LENGTH), index=True, nullable=False)

    # Quest's objective.
    # objective's type and relative object's key, separated by colon
    objective = Column(String(KEY_LENGTH + KEY_LENGTH), nullable=False)

    # objective's progress
    progress = Column(Integer, default=0)


# ------------------------------------------------------------
#
# character's honour
#
# ------------------------------------------------------------
class honours(Base):
    "All character's honours."

    __tablename__ = "honours"

    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(Integer, primary_key=True, autoincrement=True)

    # character's database id
    character = Column(Integer, unique=0, nullable=False)

    # character's honour. special character's honour is -1, such as the superuser.
    honour = Column(Integer, default=-1, index=True)
