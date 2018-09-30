
from django.contrib.admin.forms import forms
from muddery.utils.localiztion_handler import localize_form_fields
from muddery.utils.attributes_info_handler import CHARACTER_ATTRIBUTES_INFO, EQUIPMENT_ATTRIBUTES_INFO, FOOD_ATTRIBUTES_INFO
from muddery.mappings.quest_objective_set import QUEST_OBJECTIVE_SET
from muddery.mappings.quest_status_set import QUEST_STATUS_SET
from muddery.mappings.event_action_set import EVENT_ACTION_SET
from muddery.mappings.event_trigger_set import EVENT_TRIGGER_SET
from muddery.mappings.typeclass_set import TYPECLASS_SET
from muddery.worlddata.dao import model_mapper
from muddery.worlddata.dao import common_mappers as CM
from muddery.worlddata.forms.location_field import LocationField
from muddery.worlddata.forms.image_field import ImageField


def get_all_objects():
    """
    Get all objects that can be put in player's pockets.
    """
    choices = []
    for model in model_mapper.get_objects_models():
        objects = model.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])

    return choices


def get_all_pocketable_objects():
    """
    Get all objects that can be put in player's pockets.
    """
    choices = []
    for model in model_mapper.get_pocketable_object_models():
        objects = model.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])

    return choices


def generate_key(form_obj):
    """
    Generate a key for a new record.

    Args:
        form_obj: record's form.
    """
    index = 1
    if form_obj.instance.id:
        index = int(form_obj.instance.id)
    else:
        try:
            # Get last id.
            query = form_obj.Meta.model.objects.last()
            index = int(query.id)
            index += 1
        except Exception, e:
            pass

    return form_obj.instance.__class__.__name__ + "_" + str(index)


class ObjectsForm(forms.ModelForm):
    """
    Objects base form.
    """
    def clean(self):
        cleaned_data = super(ObjectsForm, self).clean()

        # check object's key
        key = cleaned_data["key"]
        if not key:
            cleaned_data["key"] = generate_key(self)
        else:
            # Check the key.
            for model in model_mapper.get_objects_models():
                if model == self.instance.__class__:
                    # Models will validate unique values of its own,
                    # so we do not validate them here.
                    continue

                try:
                    record = model.objects.get(key=key)
                except Exception, e:
                    continue

                error = forms.ValidationError("The key '%(value)s' already exists in model %(model)s.",
                                        code="unique",
                                        params={"value": key, "model": model.__name__})
                raise forms.ValidationError({"key": error})

        return cleaned_data


class GameSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GameSettingsForm, self).__init__(*args, **kwargs)
        
        choices = [("", "---------")]
        objects = CM.WORLD_ROOMS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['default_home_key'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['start_location_key'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['default_player_home_key'] = forms.ChoiceField(choices=choices, required=False)

        choices = [("", "---------")]
        objects = CM.COMMON_CHARACTERS.objects.filter(typeclass="PLAYER_CHARACTER")
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['default_player_character_key'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.GAME_SETTINGS.model
        fields = '__all__'
        list_template = "common_list.html"
        form_template = "common_form.html"


class EquipmentTypesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentTypesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = CM.EQUIPMENT_TYPES.model
        fields = '__all__'


class EquipmentPositionsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentPositionsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = CM.EQUIPMENT_POSITIONS.model
        fields = '__all__'


class WorldAreasForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(WorldAreasForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("AREA")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        self.fields['background'] = ImageField(image_type="background", required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.WORLD_AREAS.model
        fields = '__all__'
        

class WorldRoomsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(WorldRoomsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("ROOM")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = CM.WORLD_AREAS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['location'] = forms.ChoiceField(choices=choices)

        self.fields['icon'] = ImageField(image_type="icon", required=False)

        self.fields['background'] = ImageField(image_type="background", required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.WORLD_ROOMS.model
        fields = '__all__'


class WorldExitsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(WorldExitsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("EXIT")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        rooms = CM.WORLD_ROOMS.objects.all()
        choices = [(r.key, r.name + " (" + r.key + ")") for r in rooms]
        self.fields['location'] = LocationField(choices=choices)
        self.fields['destination'] = LocationField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.WORLD_EXITS.model
        fields = '__all__'


class ExitLocksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExitLocksForm, self).__init__(*args, **kwargs)

        #objects = models.world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.EXIT_LOCKS.model
        fields = '__all__'


class TwoWayExitsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TwoWayExitsForm, self).__init__(*args, **kwargs)

        #objects = models.world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.TWO_WAY_EXITS.model
        fields = '__all__'


class WorldObjectsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(WorldObjectsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("WORLD_OBJECT")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        rooms = CM.WORLD_ROOMS.objects.all()
        choices = [(r.key, r.name + " (" + r.key + ")") for r in rooms]
        self.fields['location'] = LocationField(choices=choices)

        self.fields['icon'] = ImageField(image_type="icon", required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.WORLD_OBJECTS.model
        fields = '__all__'


class WorldNPCsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(WorldNPCsForm, self).__init__(*args, **kwargs)

        # NPC's typeclass
        typeclasses = TYPECLASS_SET.get_group("NON_PLAYER")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        # NPC's location
        rooms = CM.WORLD_ROOMS.objects.all()
        choices = [(r.key, r.name + " (" + r.key + ")") for r in rooms]
        self.fields['location'] = LocationField(choices=choices)
        
        # NPC's model
        choices = [("", "---------")]
        objects = CM.CHARACTER_MODELS.objects.all().values("key", "name").distinct()
        choices.extend([(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects])
        self.fields['model'] = forms.ChoiceField(choices=choices, required=False)
        
        # NPC's icon
        self.fields['icon'] = ImageField(image_type="icon", required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.WORLD_NPCS.model
        fields = '__all__'


class ObjectCreatorsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ObjectCreatorsForm, self).__init__(*args, **kwargs)

        #objects = models.world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.OBJECT_CREATORS.model
        fields = '__all__'


class CreatorLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreatorLootListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        objects = CM.WORLD_OBJECTS.objects.filter(typeclass="WORLD_OBJECT_CREATOR")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)
        
        # depends on quest
        choices = [("", "---------")]
        objects = CM.QUESTS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.CREATOR_LOOT_LIST.model
        fields = '__all__'


class CharacterLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterLootListForm, self).__init__(*args, **kwargs)

        # providers can be world_npc or common_character
        npcs = CM.WORLD_NPCS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in npcs]

        characters = CM.COMMON_CHARACTERS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in characters])

        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        # depends on quest
        choices = [("", "---------")]
        objects = CM.QUESTS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)
        
    class Meta:
        model = CM.CHARACTER_LOOT_LIST.model
        fields = '__all__'


class QuestRewardListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestRewardListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        objects = CM.QUESTS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)
        
        # depends on quest
        choices = [("", "---------")]
        objects = CM.QUESTS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.QUEST_REWARD_LIST.model
        fields = '__all__'


class CommonObjectsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(CommonObjectsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("COMMON_OBJECT")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        self.fields['icon'] = ImageField(image_type="icon", required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.COMMON_OBJECTS.model
        fields = '__all__'


class FoodsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(FoodsForm, self).__init__(*args, **kwargs)
        
        typeclasses = TYPECLASS_SET.get_group("FOOD")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        self.fields['icon'] = ImageField(image_type="icon", required=False)

        localize_form_fields(self)
        FOOD_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = CM.FOODS.model
        fields = '__all__'
        

class SkillBooksForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(SkillBooksForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("SKILL_BOOK")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        # skills
        objects = CM.SKILLS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)
        
        # icons
        self.fields['icon'] = ImageField(image_type="icon", required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.SKILL_BOOKS.model
        fields = '__all__'


class CharacterAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True
        
        localize_form_fields(self)

    class Meta:
        model = CM.CHARACTER_ATTRIBUTES_INFO.model
        fields = '__all__'


class EquipmentAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True
        
        localize_form_fields(self)

    class Meta:
        model = CM.EQUIPMENT_ATTRIBUTES_INFO.model
        fields = '__all__'


class FoodAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FoodAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True
        
        localize_form_fields(self)

    class Meta:
        model = CM.FOOD_ATTRIBUTES_INFO.model
        fields = '__all__'


class CharacterModelsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterModelsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)
        CHARACTER_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = CM.CHARACTER_MODELS.model
        fields = '__all__'


class CommonCharacterForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(CommonCharacterForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("CHARACTER")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        # models
        choices = [("", "---------")]
        objects = CM.CHARACTER_MODELS.objects.all()
        model_keys = set([obj.key for obj in objects])
        choices.extend([(model_key, model_key) for model_key in model_keys])
        self.fields['model'] = forms.ChoiceField(choices=choices, required=False)
        
        self.fields['icon'] = ImageField(image_type="icon", required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.COMMON_CHARACTERS.model
        fields = '__all__'

    def clean(self):
        cleaned_data = super(CommonCharacterForm, self).clean()
        data_model = cleaned_data["model"]
        data_level = cleaned_data["level"]

        # check model and level
        from muddery.worlddata.dao.common_mappers import CHARACTER_MODELS

        try:
            CHARACTER_MODELS.get(key=data_model, level=data_level)
        except Exception, e:
            message = "Can not get the level data."
            levels = CHARACTER_MODELS.filter(key=data_model)
            available = [str(level.level) for level in levels]
            if len(available) == 1:
                message += " Available level: " + available[0]
            elif len(available) > 1:
                message += " Available levels: " + ", ".join(available)
            raise forms.ValidationError({"level": message})


class DefaultObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultObjectsForm, self).__init__(*args, **kwargs)

        # all character's models
        character_models = set([record.key for record in CM.CHARACTER_MODELS.objects.all()])
        choices = [(key, key) for key in character_models]
        self.fields['character'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = CM.DEFAULT_OBJECTS.model
        fields = '__all__'


class ShopsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(ShopsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("SHOP")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        self.fields['icon'] = ImageField(image_type="icon", required=False)
        
        localize_form_fields(self)
        
    class Meta:
        model = CM.SHOPS.model
        fields = '__all__'


class ShopGoodsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(ShopGoodsForm, self).__init__(*args, **kwargs)

        # all shops
        objects = CM.SHOPS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['shop'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['goods'] = forms.ChoiceField(choices=choices)

        # Goods typeclasses
        typeclasses = TYPECLASS_SET.get_group("SHOP_GOODS")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        # available units are common objects
        objects = CM.COMMON_OBJECTS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['unit'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = CM.SHOP_GOODS.model
        fields = '__all__'


class NPCShopsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NPCShopsForm, self).__init__(*args, **kwargs)

        # All NPCs.
        objects = CM.WORLD_NPCS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['npc'] = forms.ChoiceField(choices=choices)
        
        # All shops.
        objects = CM.SHOPS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['shop'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = CM.NPC_SHOPS.model
        fields = '__all__'


class SkillsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(SkillsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("SKILL")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        self.fields['icon'] = ImageField(image_type="icon", required=False)
        
        choices = [("", "---------")]
        objects = CM.SKILL_TYPES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['main_type'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['sub_type'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.SKILLS.model
        fields = '__all__'
        

class SkillTypesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SkillTypesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = CM.SKILL_TYPES.model
        fields = '__all__'


class DefaultSkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultSkillsForm, self).__init__(*args, **kwargs)

        # all character's models
        character_models = set([record.key for record in CM.CHARACTER_MODELS.objects.all()])
        choices = [(key, key) for key in character_models]
        self.fields['character'] = forms.ChoiceField(choices=choices)

        objects = CM.SKILLS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = CM.DEFAULT_SKILLS.model
        fields = '__all__'


class NPCDialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NPCDialoguesForm, self).__init__(*args, **kwargs)

        # All NPCs.
        objects = CM.WORLD_NPCS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['npc'] = forms.ChoiceField(choices=choices)
        
        objects = CM.DIALOGUES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.NPC_DIALOGUES.model
        fields = '__all__'


class QuestsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(QuestsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("QUEST")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.QUESTS.model
        fields = '__all__'


class QuestObjectivesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestObjectivesForm, self).__init__(*args, **kwargs)

        objects = CM.QUESTS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)

        objects = QUEST_OBJECTIVE_SET.all()
        choices = [(obj, obj) for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.QUEST_OBJECTIVES.model
        fields = '__all__'


class QuestDependenciesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestDependenciesForm, self).__init__(*args, **kwargs)

        objects = CM.QUESTS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)
        self.fields['dependency'] = forms.ChoiceField(choices=choices)
        
        objects = QUEST_STATUS_SET.all()
        choices = [(obj, obj) for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.QUEST_DEPENDENCIES.model
        fields = '__all__'


class DialogueQuestDependenciesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueQuestDependenciesForm, self).__init__(*args, **kwargs)

        objects = CM.DIALOGUES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        
        objects = CM.QUESTS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dependency'] = forms.ChoiceField(choices=choices)
        
        objects = QUEST_STATUS_SET.all()
        choices = [obj for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.DIALOGUE_QUEST_DEPENDENCIES.model
        fields = '__all__'


class EquipmentsForm(ObjectsForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentsForm, self).__init__(*args, **kwargs)

        typeclasses = TYPECLASS_SET.get_group("EQUIPMENT")
        choices = [(key, cls.typeclass_name + " (" + key + ")") for key, cls in typeclasses.items()]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        objects = CM.EQUIPMENT_POSITIONS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['position'] = forms.ChoiceField(choices=choices)
        
        objects = CM.EQUIPMENT_TYPES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        self.fields['icon'] = ImageField(image_type="icon", required=False)
        
        localize_form_fields(self)
        EQUIPMENT_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = CM.EQUIPMENTS.model
        fields = '__all__'


class EventDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDataForm, self).__init__(*args, **kwargs)

        objects = EVENT_ACTION_SET.all()
        choices = [(obj, obj) for obj in objects]
        self.fields['action'] = forms.ChoiceField(choices=choices)

        objects = EVENT_TRIGGER_SET.all()
        choices = [(obj, obj) for obj in objects]
        self.fields['trigger_type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    def clean(self):
        cleaned_data = super(EventDataForm, self).clean()

        # check object's key
        key = cleaned_data["key"]
        if not key:
            cleaned_data["key"] = generate_key(self)
        
    class Meta:
        model = CM.EVENT_DATA.model
        fields = '__all__'


class ActionAttackForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ActionAttackForm, self).__init__(*args, **kwargs)

        objects = CM.EVENT_DATA.objects.filter(action="ACTION_ATTACK")
        choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
        self.fields['event_key'] = forms.ChoiceField(choices=choices)
        
        objects = CM.COMMON_CHARACTERS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['mob'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.ACTION_ATTACK.model
        fields = '__all__'


class ActionDialogueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ActionDialogueForm, self).__init__(*args, **kwargs)

        objects = CM.EVENT_DATA.objects.filter(action="ACTION_DIALOGUE")
        choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
        self.fields['event_key'] = forms.ChoiceField(choices=choices)

        objects = CM.DIALOGUES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        # NPCs
        choices = [("", "---------")]
        objects = CM.WORLD_NPCS.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['npc'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.ACTION_DIALOGUE.model
        fields = '__all__'


class ActionLearnSkillForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ActionLearnSkillForm, self).__init__(*args, **kwargs)

        objects = CM.EVENT_DATA.objects.filter(action="ACTION_LEARN_SKILL")
        choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
        self.fields['event_key'] = forms.ChoiceField(choices=choices)

        objects = CM.SKILLS.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.ACTION_LEARN_SKILL.model
        fields = '__all__'


class DialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialoguesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    def clean(self):
        cleaned_data = super(DialoguesForm, self).clean()

        # check object's key
        key = cleaned_data["key"]
        if not key:
            cleaned_data["key"] = generate_key(self)

    class Meta:
        model = CM.DIALOGUES.model
        fields = '__all__'


class DialogueRelationsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueRelationsForm, self).__init__(*args, **kwargs)

        objects = CM.DIALOGUES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        self.fields['next_dlg'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.DIALOGUE_RELATIONS.model
        fields = '__all__'


class DialogueSentencesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueSentencesForm, self).__init__(*args, **kwargs)

        objects = CM.DIALOGUES.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        # dialogue's icon
        self.fields['icon'] = ImageField(image_type="icon", required=False)

        localize_form_fields(self)

    def clean(self):
        cleaned_data = super(DialogueSentencesForm, self).clean()

        # check object's key
        key = cleaned_data["key"]
        if not key:
            cleaned_data["key"] = generate_key(self)

    class Meta:
        model = CM.DIALOGUE_SENTENCES.model
        fields = '__all__'


class ConditionDescForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConditionDescForm, self).__init__(*args, **kwargs)

        choices = get_all_objects()
        self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.CONDITION_DESC.model
        fields = '__all__'
        

class LocalizedStringsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LocalizedStringsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = CM.LOCALIZED_STRINGS.model
        fields = '__all__'


class ImageResourcesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImageResourcesForm, self).__init__(*args, **kwargs)

        choices = [("background", "background"),
                   ("icon", "icon")]
        self.fields['type'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = CM.IMAGE_RESOURCES.model
        fields = '__all__'
