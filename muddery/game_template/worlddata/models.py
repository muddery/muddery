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
    action = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        verbose_name = "World Object List"
        verbose_name_plural = "World Object List"


#------------------------------------------------------------
#
# store all spawners
#
#------------------------------------------------------------
class object_creaters(models.Model):
    "Store all object creaters."

    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    home = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)
    obj_list = models.TextField(blank=True)
    action = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        verbose_name = "World Object List"
        verbose_name_plural = "World Object List"


#------------------------------------------------------------
#
# store all common objects
#
#------------------------------------------------------------
class common_objects(models.Model):
    "Store all common objects."
    
    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    max_stack = models.IntegerField(blank=True, default=1)
    unique = models.BooleanField(blank=True, default=False)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)
    action = models.TextField(blank=True)
    effect = models.TextField(blank=True)
    
    class Meta:
        "Define Django meta options"
        verbose_name = "Common Object List"
        verbose_name_plural = "Common Object List"


#------------------------------------------------------------
#
# store all foods
#
#------------------------------------------------------------
class foods(models.Model):
    "Store all foods."
    
    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    max_stack = models.IntegerField(blank=True, default=1)
    unique = models.BooleanField(blank=True, default=False)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)
    action = models.TextField(blank=True)
    effect = models.TextField(blank=True)
    
    class Meta:
        "Define Django meta options"
        verbose_name = "Food List"
        verbose_name_plural = "Food List"


#------------------------------------------------------------
#
# store all equip_types
#
#------------------------------------------------------------
class equip_types(models.Model):
    "Store all equip types."
    
    type = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    career = models.CharField(max_length=255, blank=True)
    
    class Meta:
        "Define Django meta options"
        verbose_name = "Equipment List"
        verbose_name_plural = "Equipment List"


#------------------------------------------------------------
#
# store all equipments
#
#------------------------------------------------------------
class equipments(models.Model):
    "Store all equipments."
    
    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    max_stack = models.IntegerField(blank=True, default=1)
    unique = models.BooleanField(blank=True, default=False)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)
    action = models.TextField(blank=True)
    effect = models.TextField(blank=True)
    position = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)
    
    class Meta:
        "Define Django meta options"
        verbose_name = "Equipment List"
        verbose_name_plural = "Equipment List"


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
class dialogues(models.Model):
    "Store all unique objects."
    
    dialogue = models.CharField(max_length=255)
    sentence = models.IntegerField()
    speaker = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    next = models.CharField(max_length=255, blank=True)
    condition = models.TextField(blank=True)
    action = models.TextField(blank=True)

    class Meta:
        "Define Django meta options"
        verbose_name = "World Dialogue List"
        verbose_name_plural = "World Dialogue List"
