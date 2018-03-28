
from __future__ import print_function

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings


#------------------------------------------------------------
#
# character's honour
#
#------------------------------------------------------------
class honours(models.Model):
    "All character's honours."
   
    # character's database id
    character = models.IntegerField(unique=True)
    
    # character's honour. special character's honour is -1, such as the superuser.
    honour = models.IntegerField(blank=True, default=-1, db_index=True)

    class Meta:
        "Define Django meta options"
        abstract = True
        verbose_name = "Honour"
        verbose_name_plural = "Honours"
