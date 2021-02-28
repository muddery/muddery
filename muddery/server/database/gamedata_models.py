
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
