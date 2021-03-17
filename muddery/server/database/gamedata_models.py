
from django.db import models

KEY_LENGTH = 255
NAME_LENGTH = 80


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
        verbose_name = "Object Key"
        verbose_name_plural = "Object Keys"


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
        verbose_name = "Object Attribute"
        verbose_name_plural = "Object Attributes"
        unique_together = ("obj_id", "key")


# ------------------------------------------------------------
#
# Game object's runtime attributes.
#
# ------------------------------------------------------------
class object_status(BaseAttributes):

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        verbose_name = "Object Runtime Status"
        verbose_name_plural = "Object Runtime Status"
        unique_together = ("obj_id", "key")


# ------------------------------------------------------------
#
# player character's data
#
# ------------------------------------------------------------
class player_character(models.Model):
    "Player character's data."

    # character's database id
    object_id = models.PositiveIntegerField(unique=True)

    # character's nickname
    nickname = models.CharField(max_length=KEY_LENGTH)

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        verbose_name = "Player Character"
        verbose_name_plural = "Player Characters"


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
        verbose_name = "Character's Inventory"
        verbose_name_plural = "Character's Inventories"
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
        verbose_name = "Character Skill"
        verbose_name_plural = "Character Skills"
        unique_together = ("character_id", "skill")


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
        verbose_name = "Quest"
        verbose_name_plural = "Quests"
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
        verbose_name = "Quest Objective"
        verbose_name_plural = "Quest Objectives"
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
        verbose_name = "Honour"
        verbose_name_plural = "Honours"
