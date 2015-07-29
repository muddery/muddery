from django.db import models


#------------------------------------------------------------
#
# store all rooms
#
#------------------------------------------------------------
class world_rooms(models.Model):
    "Store all unique rooms."

    # It must have these fields.
    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)

    # You can add custom fields here.

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

    # It must have these fields.
    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)
    destination = models.CharField(max_length=255, blank=True)

    # You can add custom fields here.

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

    # It must have these fields.
    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)
    action = models.TextField(blank=True)

    # You can add custom fields here.

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

    # It must have these fields.
    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)
    obj_list = models.TextField(blank=True)
    action = models.TextField(blank=True)

    # You can add custom fields here.

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

    # It must have these fields.
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

    # You can add custom fields here.

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

    # It must have these fields.
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
    hp = models.IntegerField(blank=True, default=0)
    mp = models.IntegerField(blank=True, default=0)

    # You can add custom fields here.
    hp = models.IntegerField(blank=True, default=0)

    class Meta:
        "Define Django meta options"
        verbose_name = "Food List"
        verbose_name_plural = "Food List"


#------------------------------------------------------------
#
# store all equip_types
#
#------------------------------------------------------------
class equipment_types(models.Model):
    "Store all equip types."

    # It must have these fields.
    type = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    career = models.CharField(max_length=255, blank=True)

    # You can add custom fields here.

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

    # It must have these fields.
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
    position = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, blank=True)
    effect = models.TextField(blank=True)

    # You can add custom fields here.
    attack = models.IntegerField(blank=True, default=0)
    defence = models.IntegerField(blank=True, default=0)

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

    # It must have these fields.
    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    dialogue = models.CharField(max_length=255, blank=True)
    lock = models.CharField(max_length=255, blank=True)
    attributes = models.TextField(blank=True)

    # You can add custom fields here.

    class Meta:
        "Define Django meta options"
        verbose_name = "World NPC List"
        verbose_name_plural = "World NPC List"


#------------------------------------------------------------
#
# store all skills
#
#------------------------------------------------------------
class skills(models.Model):
    "Store all skills."

    # It must have these fields.
    key = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    typeclass = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    cd = models.IntegerField(blank=True, default=0)
    passive = models.BooleanField(blank=True, default=False)
    condition = models.TextField(blank=True)
    function = models.CharField(max_length=255)
    effect = models.FloatField(blank=True, default=0)

    # You can add custom fields here.

    class Meta:
        "Define Django meta options"
        verbose_name = "Skill"
        verbose_name_plural = "Skills"


#------------------------------------------------------------
#
# store all dialogues
#
#------------------------------------------------------------
class dialogues(models.Model):
    "Store all dialogues."

    # It must have these fields.
    dialogue = models.CharField(max_length=255, db_index=True)
    sentence = models.IntegerField()
    speaker = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    next = models.CharField(max_length=255, blank=True)
    condition = models.TextField(blank=True)
    action = models.TextField(blank=True)

    # You can add custom fields here.

    class Meta:
        "Define Django meta options"
        verbose_name = "World Dialogue List"
        verbose_name_plural = "World Dialogue List"
        unique_together = (("dialogue", "sentence"),)


#------------------------------------------------------------
#
# character levels
#
#------------------------------------------------------------
class character_level(models.Model):
    "Store all character level informations."

    # It must have these fields.
    level = models.IntegerField(primary_key=True)
    max_exp = models.IntegerField()

    # You can add custom fields here.
    max_hp = models.IntegerField()
    max_mp = models.IntegerField()
    attack = models.IntegerField()
    defence = models.IntegerField()

    class Meta:
        "Define Django meta options"
        verbose_name = "Character Level List"
        verbose_name_plural = "Character Level List"


#------------------------------------------------------------
#
# local strings
#
#------------------------------------------------------------
class localized_strings(models.Model):
    "Store all server local strings informations."

    # It must have these fields.
    origin = models.TextField(primary_key=True)
    local = models.TextField(blank=True)

    # You can add custom fields here.

    class Meta:
        "Define Django meta options"
        verbose_name = "Server Local String"
        verbose_name_plural = "Server Local Strings"
