
from django.db import models

KEY_LENGTH = 255


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
