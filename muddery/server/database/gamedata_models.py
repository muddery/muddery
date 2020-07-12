
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings

KEY_LENGTH = 255
TYPE_LENGTH = 80


# ------------------------------------------------------------
#
# Game's basic settings.
#
# ------------------------------------------------------------
class object_attributes(models.Model):
    """
    Game's basic settings.
    NOTE: Only uses the first record!
    """
    # object's id
    obj_id = models.PositiveIntegerField(db_index=True)

    # attribute's name
    key = models.CharField(max_length=KEY_LENGTH, db_index=True)

    # attribute's type
    type = models.CharField(max_length=TYPE_LENGTH)

    # In solo mode, a player can not see or affect other players.
    value = models.TextField()

    class Meta:
        "Define Django meta options"
        abstract = True
        app_label = "gamedata"
        verbose_name = "Object Attribute"
        verbose_name_plural = "Object Attributes"
        unique_together = ("obj_id", "key")
