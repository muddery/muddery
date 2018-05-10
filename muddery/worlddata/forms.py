
from django.contrib.admin.forms import forms
from muddery.utils.localiztion_handler import localize_form_fields
from muddery.utils.attributes_info_handler import CHARACTER_ATTRIBUTES_INFO, EQUIPMENT_ATTRIBUTES_INFO, FOOD_ATTRIBUTES_INFO
from muddery.mappings.typeclass_set import TYPECLASS_SET
from muddery.worlddata.dao import general_mapper
from muddery.worlddata.dao import model_mapper
from muddery.mappings.form_set import form_mapping


def get_all_objects():
    """
    Get all objects that can be put in player's pockets.
    """
    choices = []
    for data in general_mapper.get_all_models():
        objects = data.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])

    return choices
    
    
def get_all_pocketable_objects():
    """
    Get all objects that can be put in player's pockets.
    """
    # available objects are common objects, foods skill books or equipments
    objects = model_mapper.COMMON_OBJECTS.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]

    foods = model_mapper.FOODS.objects.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in foods])

    skill_books = model_mapper.SKILL_BOOKS.objects.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in skill_books])

    equipments = model_mapper.EQUIPMENTS.objects.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in equipments])

    return choices


@form_mapping
class GameSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GameSettingsForm, self).__init__(*args, **kwargs)
        
        choices = [("", "---------")]
        objects = model_mapper.WORLD_ROOMS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['default_home_key'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['start_location_key'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['default_player_home_key'] = forms.ChoiceField(choices=choices, required=False)

        choices = [("", "---------")]
        objects = model_mapper.COMMON_CHARACTERS.objects.filter(typeclass="CLASS_PLAYER")
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['default_player_character_key'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.GAME_SETTINGS.model
        fields = '__all__'
        list_template = "common_list.html"
        form_template = "common_form.html"


@form_mapping
class EquipmentPositionsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentPositionsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.EQUIPMENT_POSITIONS.model
        fields = '__all__'


@form_mapping
class WorldAreasForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldAreasForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("AREA")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = model_mapper.IMAGE_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['background'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.WORLD_AREAS.model
        fields = '__all__'
        

@form_mapping
class WorldRoomsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldRoomsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("ROOM")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = model_mapper.WORLD_AREAS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['location'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        choices = [("", "---------")]
        objects = model_mapper.IMAGE_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['background'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.WORLD_ROOMS.model
        fields = '__all__'


@form_mapping
class WorldExitsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldExitsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("EXIT")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        areas = model_mapper.WORLD_AREAS.objects.all()
        rooms = model_mapper.WORLD_ROOMS.objects.all()
        choices = []
        for area in areas:
            area_rooms = [(r.key, r.name + " (" + r.key + ")") for r in rooms if r.location == area.key]
            if area_rooms:
                choices.append((area.name, area_rooms))
        self.fields['location'] = forms.ChoiceField(choices=choices)
        self.fields['destination'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.WORLD_EXITS.model
        fields = '__all__'


@form_mapping
class ExitLocksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExitLocksForm, self).__init__(*args, **kwargs)

        #objects = models.world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.EXIT_LOCKS.model
        fields = '__all__'


@form_mapping
class TwoWayExitsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TwoWayExitsForm, self).__init__(*args, **kwargs)

        #objects = models.world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.TWO_WAY_EXITS.model
        fields = '__all__'


@form_mapping
class WorldObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldObjectsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("WORLD_OBJECT")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        areas = model_mapper.WORLD_AREAS.objects.all()
        rooms = model_mapper.WORLD_ROOMS.objects.all()
        choices = []
        for area in areas:
            area_rooms = [(r.key, r.name + " (" + r.key + ")") for r in rooms if r.location == area.key]
            if area_rooms:
                choices.append((area.name, area_rooms))
        self.fields['location'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.WORLD_OBJECTS.model
        fields = '__all__'


@form_mapping
class WorldNPCsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldNPCsForm, self).__init__(*args, **kwargs)

        # NPC's typeclass
        typeclasses = TYPECLASS_SET.get_group("NON_PLAYER")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        # NPC's location
        areas = model_mapper.WORLD_AREAS.objects.all()
        rooms = model_mapper.WORLD_ROOMS.objects.all()
        choices = []
        for area in areas:
            area_rooms = [(r.key, r.name + " (" + r.key + ")") for r in rooms if r.location == area.key]
            if area_rooms:
                choices.append((area.name, area_rooms))
        self.fields['location'] = forms.ChoiceField(choices=choices)
        
        # NPC's model
        choices = [("", "---------")]
        objects = model_mapper.CHARACTER_MODELS.objects.all().values("key", "name").distinct()
        choices.extend([(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects])
        self.fields['model'] = forms.ChoiceField(choices=choices, required=False)
        
        # NPC's icon
        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.WORLD_NPCS.model
        fields = '__all__'


@form_mapping
class ObjectCreatorsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ObjectCreatorsForm, self).__init__(*args, **kwargs)

        #objects = models.world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.OBJECT_CREATORS.model
        fields = '__all__'


@form_mapping
class CreatorLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreatorLootListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        objects = model_mapper.WORLD_OBJECTS.objects.filter(typeclass="WORLD_OBJECT_CREATOR")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)
        
        # depends on quest
        choices = [("", "---------")]
        objects = model_mapper.QUESTS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.CREATOR_LOOT_LIST.model
        fields = '__all__'


@form_mapping
class CharacterLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterLootListForm, self).__init__(*args, **kwargs)

        # providers can be world_npc or common_character
        npcs = model_mapper.WORLD_NPCS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in npcs]

        characters = model_mapper.COMMON_CHARACTERS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in characters])

        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        # depends on quest
        choices = [("", "---------")]
        objects = model_mapper.QUESTS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.CHARACTER_LOOT_LIST.model
        fields = '__all__'


@form_mapping
class QuestRewardListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestRewardListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        objects = model_mapper.QUESTS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)
        
        # depends on quest
        choices = [("", "---------")]
        objects = model_mapper.QUESTS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.QUEST_REWARD_LIST.model
        fields = '__all__'


@form_mapping
class CommonObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommonObjectsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("COMMON_OBJECT")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.COMMON_OBJECTS.model
        fields = '__all__'


@form_mapping
class FoodsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FoodsForm, self).__init__(*args, **kwargs)
        
        typeclasses = TYPECLASS_SET.get_group("FOOD")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)
        FOOD_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = model_mapper.FOODS.model
        fields = '__all__'
        

@form_mapping
class SkillBooksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SkillBooksForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("SKILL_BOOK")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        # skills
        objects = model_mapper.SKILLS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)
        
        # icons
        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.SKILL_BOOKS.model
        fields = '__all__'


@form_mapping
class CharacterAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True;
        
        localize_form_fields(self)

    class Meta:
        model = model_mapper.CHARACTER_ATTRIBUTES_INFO.model
        fields = '__all__'


@form_mapping
class EquipmentAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True;
        
        localize_form_fields(self)

    class Meta:
        model = model_mapper.EQUIPMENT_ATTRIBUTES_INFO.model
        fields = '__all__'


@form_mapping
class FoodAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FoodAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True;
        
        localize_form_fields(self)

    class Meta:
        model = model_mapper.FOOD_ATTRIBUTES_INFO.model
        fields = '__all__'


@form_mapping
class CharacterModelsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterModelsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)
        CHARACTER_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = model_mapper.CHARACTER_MODELS.model
        fields = '__all__'


@form_mapping
class CommonCharacterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommonCharacterForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("CHARACTER")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        # models
        choices = [("", "---------")]
        objects = model_mapper.CHARACTER_MODELS.objects.all()
        model_keys = set([obj.key for obj in objects])
        choices.extend([(model_key, model_key) for model_key in model_keys])
        self.fields['model'] = forms.ChoiceField(choices=choices, required=False)
        
        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.COMMON_CHARACTERS.model
        fields = '__all__'


@form_mapping
class DefaultObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultObjectsForm, self).__init__(*args, **kwargs)

        # all character's models
        character_models = set([record.key for record in model_mapper.CHARACTER_MODELS.objects.all()])
        choices = [(key, key) for key in character_models]
        self.fields['character'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.DEFAULT_OBJECTS.model
        fields = '__all__'


@form_mapping
class ShopsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShopsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("SHOP")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.SHOPS.model
        fields = '__all__'


@form_mapping
class ShopGoodsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShopGoodsForm, self).__init__(*args, **kwargs)

        # all shops
        objects = model_mapper.SHOPS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['shop'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        # Goods typeclasses
        typeclasses = TYPECLASS_SET.get_group("SHOP_GOODS")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        # available units are common objects
        objects = model_mapper.COMMON_OBJECTS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['unit'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.SHOP_GOODS.model
        fields = '__all__'


@form_mapping
class NPCShopsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NPCShopsForm, self).__init__(*args, **kwargs)

        # All NPCs.
        objects = model_mapper.WORLD_NPCS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['npc'] = forms.ChoiceField(choices=choices)
        
        # All shops.
        objects = model_mapper.SHOPS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['shop'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.NPC_SHOPS.model
        fields = '__all__'


@form_mapping
class SkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SkillsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("SKILL")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        choices = [("", "---------")]
        objects = model_mapper.SKILL_TYPES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['main_type'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['sub_type'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.SKILLS.model
        fields = '__all__'
        

@form_mapping
class SkillTypesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SkillTypesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.SKILL_TYPES.model
        fields = '__all__'


@form_mapping
class DefaultSkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultSkillsForm, self).__init__(*args, **kwargs)

        # all character's models
        character_models = set([record.key for record in model_mapper.CHARACTER_MODELS.objects.all()])
        choices = [(key, key) for key in character_models]
        self.fields['character'] = forms.ChoiceField(choices=choices)

        objects = model_mapper.SKILLS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.DEFAULT_SKILLS.model
        fields = '__all__'


@form_mapping
class NPCDialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NPCDialoguesForm, self).__init__(*args, **kwargs)

        # All NPCs.
        objects = model_mapper.WORLD_NPCS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['npc'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.DIALOGUES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.NPC_DIALOGUES.model
        fields = '__all__'


@form_mapping
class QuestsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("QUEST")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.QUESTS.model
        fields = '__all__'


@form_mapping
class QuestObjectivesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestObjectivesForm, self).__init__(*args, **kwargs)

        objects = model_mapper.QUESTS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)

        objects = model_mapper.QUEST_OBJECTIVE_TYPES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.QUEST_OBJECTIVES.model
        fields = '__all__'


@form_mapping
class QuestDependenciesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestDependenciesForm, self).__init__(*args, **kwargs)

        objects = model_mapper.QUESTS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)
        self.fields['dependency'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.QUEST_DEPENDENCY_TYPES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.QUEST_DEPENDENCIES.model
        fields = '__all__'


@form_mapping
class DialogueQuestDependenciesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueQuestDependenciesForm, self).__init__(*args, **kwargs)

        objects = model_mapper.DIALOGUES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.QUESTS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dependency'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.QUEST_DEPENDENCY_TYPES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.DIALOGUE_QUEST_DEPENDENCIES.model
        fields = '__all__'


@form_mapping
class EquipmentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("EQUIPMENT")
        choices = [(key, value["name"] + " (" + key + ")") for key, value in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        objects = model_mapper.EQUIPMENT_POSITIONS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['position'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.EQUIPMENT_TYPES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        localize_form_fields(self)
        EQUIPMENT_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = model_mapper.EQUIPMENTS.model
        fields = '__all__'


@form_mapping
class EventDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDataForm, self).__init__(*args, **kwargs)

        objects = model_mapper.EVENT_TYPES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        objects = model_mapper.EVENT_TRIGGER_TYPES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['trigger_type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.EVENT_DATA.model
        fields = '__all__'


@form_mapping
class EventAttacksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventAttacksForm, self).__init__(*args, **kwargs)

        objects = model_mapper.EVENT_DATA.objects.filter(type="EVENT_ATTACK")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['key'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.COMMON_CHARACTERS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['mob'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.EVENT_ATTACKS.model
        fields = '__all__'


@form_mapping
class EventDialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDialoguesForm, self).__init__(*args, **kwargs)

        objects = model_mapper.EVENT_DATA.objects.filter(type="EVENT_DIALOGUE")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['key'] = forms.ChoiceField(choices=choices)

        objects = model_mapper.DIALOGUES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        # NPCs
        choices = [("", "---------")]
        objects = model_mapper.WORLD_NPCS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['npc'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.EVENT_DIALOGUES.model
        fields = '__all__'


@form_mapping
class DialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialoguesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.DIALOGUES.model
        fields = '__all__'


@form_mapping
class DialogueRelationsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueRelationsForm, self).__init__(*args, **kwargs)

        objects = model_mapper.DIALOGUES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        self.fields['next_dlg'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.DIALOGUE_RELATIONS.model
        fields = '__all__'


@form_mapping
class DialogueSentencesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueSentencesForm, self).__init__(*args, **kwargs)

        objects = model_mapper.DIALOGUES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        # dialogue's icon
        choices = [("", "---------")]
        objects = model_mapper.ICON_RESOURCES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        choices = [("", "---------")]
        objects = model_mapper.QUESTS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['provide_quest'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['complete_quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.DIALOGUE_SENTENCES.model
        fields = '__all__'


@form_mapping
class ConditionDescForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConditionDescForm, self).__init__(*args, **kwargs)

        choices = get_all_objects()
        self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.CONDITION_DESC.model
        fields = '__all__'
        

@form_mapping
class LocalizedStringsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LocalizedStringsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.LOCALIZED_STRINGS.model
        fields = '__all__'


@form_mapping
class ImageResourcesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImageResourcesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.IMAGE_RESOURCES.model
        fields = ('key', 'name', 'resource',)


@form_mapping
class IconResourcesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(IconResourcesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.ICON_RESOURCES.model
        fields = ('key', 'name', 'resource',)
