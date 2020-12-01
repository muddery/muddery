
from django.db import models

KEY_LENGTH = 255


# ------------------------------------------------------------
#
# Game object's runtime attributes.
#
# ------------------------------------------------------------
class BaseAttributes(models.Model):
    """
    Game's basic settings.
    NOTE: Only uses the first record!
    """
    # object's type
    obj_type = models.CharField(max_length=KEY_LENGTH, db_index=True)

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
        unique_together = ("obj_type", "obj_id", "key")
