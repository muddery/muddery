
from django.db import models


KEY_LENGTH = 80
NAME_LENGTH = 80


class system_data(models.Model):
    """
    Store system data. Only use the first record.
    """
    # The last id of accounts.
    last_account_id = models.PositiveIntegerField(default=0)

    # The last id of player characters.
    last_player_character_id = models.PositiveIntegerField(default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"


# ------------------------------------------------------------
#
# Set object's key.
#
# ------------------------------------------------------------
class object_keys(models.Model):
    # object's id
    object_id = models.PositiveIntegerField(unique=True)

    # object's key
    object_key = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # world unique object's type
    unique_type = models.CharField(max_length=KEY_LENGTH, blank=True, null=True, db_index=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"


# ------------------------------------------------------------
#
# The base of runtime attributes.
#
# ------------------------------------------------------------
class BaseAttributes(models.Model):
    """
    Object's runtime attributes.
    """
    # object's id
    obj_id = models.PositiveIntegerField(db_index=True)

    # attribute's name
    key = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # In solo mode, a player can not see or affect other players.
    value = models.TextField()

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        unique_together = ("obj_id", "key")


# ------------------------------------------------------------
#
# Game object's runtime attributes.
#
# ------------------------------------------------------------
class object_states(BaseAttributes):

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        unique_together = ("obj_id", "key")


# ------------------------------------------------------------
#
# server bans
#
# ------------------------------------------------------------
class server_bans(models.Model):

    # ban's type, should be "IP" or "USERNAME"
    type = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # IP or name
    target = models.CharField(max_length=KEY_LENGTH)

    # create time
    create_time = models.DateTimeField(auto_now_add=True)

    # finish time
    finish_time = models.DateTimeField()

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        unique_together = ("type", "target")


# ------------------------------------------------------------
#
# player's accounts
#
# ------------------------------------------------------------
class accounts(models.Model):

    # account's username
    username = models.CharField(max_length=KEY_LENGTH, unique=True)

    # account's password
    password = models.CharField(max_length=128)

    # account's id
    account_id = models.PositiveIntegerField(unique=True)

    # account's type
    type = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # account's create time
    create_time = models.DateTimeField(blank=True, null=True)

    # account's last login time
    last_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"


# ------------------------------------------------------------
#
# player account's characters
#
# ------------------------------------------------------------
class account_characters(models.Model):
    "Player character's data."
    # player's account id
    account_id = models.PositiveIntegerField(db_index=True)

    # playable character's id
    char_id = models.PositiveIntegerField(unique=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"


# ------------------------------------------------------------
#
# player character's basic information
#
# ------------------------------------------------------------
class character_info(models.Model):
    "player character's basic information"

    # playable character's id
    char_id = models.PositiveIntegerField(unique=True)

    # character's nickname
    nickname = models.CharField(max_length=KEY_LENGTH)

    # character's level
    level = models.PositiveIntegerField(default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"


# ------------------------------------------------------------
#
# player character's info
#
# ------------------------------------------------------------
class character_location(models.Model):
    "player character's location"

    # player character's id
    char_id = models.PositiveIntegerField(unique=True)

    # location (room's key)
    location = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"


# ------------------------------------------------------------
#
# player character's inventory
#
# ------------------------------------------------------------
class character_inventory(models.Model):
    "Player character's inventory."

    # character's id
    character_id = models.PositiveIntegerField(db_index=True)

    # position in the inventory
    position = models.PositiveIntegerField()

    # object's key
    object_key = models.CharField(max_length=KEY_LENGTH)

    # object's number
    number = models.PositiveIntegerField(default=0)

    # object's level
    level = models.PositiveIntegerField(null=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        unique_together = ("character_id", "position")


# ------------------------------------------------------------
#
# player character's equipments
#
# ------------------------------------------------------------
class character_equipments(models.Model):
    "Player character's equipments."

    # character's id
    character_id = models.PositiveIntegerField(db_index=True)

    # the position to put on equipments
    position = models.CharField(max_length=KEY_LENGTH)

    # object's key
    object_key = models.CharField(max_length=KEY_LENGTH)

    # object's level
    level = models.PositiveIntegerField(null=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        unique_together = ("character_id", "position")


# ------------------------------------------------------------
#
# player character's skills
#
# ------------------------------------------------------------
class character_skills(models.Model):
    "Player character's skills."

    # character's id
    character_id = models.PositiveIntegerField(db_index=True)

    # skill's key
    skill = models.CharField(max_length=KEY_LENGTH)

    # skill's level
    level = models.PositiveIntegerField(null=True)

    # is default skill
    is_default = models.BooleanField(default=False)

    # CD's finish time
    cd_finish = models.PositiveIntegerField(default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        unique_together = ("character_id", "skill")


# ------------------------------------------------------------
#
# player character's combat information
#
# ------------------------------------------------------------
class character_combat(models.Model):
    "Player character's combat."

    # character's id
    character_id = models.PositiveIntegerField(unique=True)

    # combat's id
    combat = models.PositiveIntegerField()

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"


# ------------------------------------------------------------
#
# player character's quests
#
# ------------------------------------------------------------
class character_quests(models.Model):
    "Player character's quests."

    # character's id
    character_id = models.PositiveIntegerField(db_index=True)

    # quest's key
    quest = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # quest is finished
    finished = models.BooleanField(default=False, db_index=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        unique_together = ("character_id", "quest")


# ------------------------------------------------------------
#
# quest objectives
#
# ------------------------------------------------------------
class quest_objectives(models.Model):
    "Quests' objectives."

    # character's id and quest's key, separated by colon
    character_quest = models.CharField(max_length=KEY_LENGTH+KEY_LENGTH, db_index=True)

    # Quest's objective.
    # objective's type and relative object's key, separated by colon
    objective = models.CharField(max_length=KEY_LENGTH+KEY_LENGTH)

    # objective's progress
    progress = models.PositiveIntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        unique_together = ("character_quest", "objective")


# ------------------------------------------------------------
#
# character's honour
#
# ------------------------------------------------------------
class honours(models.Model):
    "All character's honours."

    # character's database id
    character = models.IntegerField(unique=True)

    # character's honour. special character's honour is -1, such as the superuser.
    honour = models.IntegerField(blank=True, default=-1, db_index=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
