from django.db import models


#------------------------------------------------------------
#
# store all rooms
#
#------------------------------------------------------------
class world_rooms(models.Model):
    "Store all unique rooms."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    home = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        verbose_name = "World Room List"
        verbose_name_plural = "World Room List"


#------------------------------------------------------------
#
# store all exits
#
#------------------------------------------------------------
class world_exits(models.Model):
    "Store all unique exits."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    home = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)
    destination = models.CharField(max_length=255, blank=True)

    class Meta:
        "Define Django meta options"
        verbose_name = "World Exit List"
        verbose_name_plural = "World Exit List"


#------------------------------------------------------------
#
# store all objects
#
#------------------------------------------------------------
class world_objects(models.Model):
    "Store all unique objects."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    home = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        verbose_name = "World Object List"
        verbose_name_plural = "World Object List"


#------------------------------------------------------------
#
# store all npcs
#
#------------------------------------------------------------
class world_npcs(models.Model):
    "Store all unique objects."
    
    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    home = models.CharField(max_length=255, blank=True)
    dialogue = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        verbose_name = "World NPC List"
        verbose_name_plural = "World NPC List"



#------------------------------------------------------------
#
# store all dialogues
#
#------------------------------------------------------------
class world_dialogues(models.Model):
    "Store all unique objects."
    
    dialogue = models.CharField(max_length=255, primary_key=True)
    sentence = models.CharField(max_length=255, primary_key=True)
    speaker = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    next = models.CharField(max_length=255, blank=True)
    condition = models.TextField(blank=True)
    action = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        verbose_name = "World Dialogue List"
        verbose_name_plural = "World Dialogue List"


#------------------------------------------------------------
#
# store all details
#
#------------------------------------------------------------
class world_details(models.Model):
    "Store all details."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        "Define Django meta options"
        verbose_name = "World Detail List"
        verbose_name_plural = "World Detail List"


#------------------------------------------------------------
#
# store all personal objects
#
#------------------------------------------------------------
class personal_objects(models.Model):
    "Store all personal objects."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    home = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        verbose_name = "Personal Object List"
        verbose_name_plural = "Personal Object List"

