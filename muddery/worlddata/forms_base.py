
from django.contrib.admin.forms import forms
from muddery.utils.localiztion_handler import localize_form_fields
from muddery.worlddata.data_sets import DATA_SETS


def exist_key(key, except_models=None):
    """
    Check if the key exists.
    """
    if key[:2] == "__":
        # Keys begin with __ are reserved by system.
        return True

    # Get models.
    for data_settings in DATA_SETS.object_data:
        if data_settings.model_name in except_models:
            continue
        try:
            data_settings.model.objects.get(key=key)
            return True
        except Exception, e:
            continue

    return False


def get_all_pocketable_objects():
    """
    Get all objects that can be put in player's pockets.
    """
    # available objects are common objects, foods skill books or equipments
    objects = DATA_SETS.common_objects.objects.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]

    foods = DATA_SETS.foods.objects.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in foods])

    skill_books = DATA_SETS.skill_books.objects.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in skill_books])

    equipments = DATA_SETS.equipments.objects.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in equipments])

    return choices


class UniqueKeyForm(forms.ModelForm):
    """
    Unique key form can create a default key and checks the key.
    """
    def clean(self):
        "Validate values."
        cleaned_data = super(UniqueKeyForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if exist_key(key, except_models=[self.Meta.model.__name__]):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])

        return cleaned_data
        
        
class GameSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GameSettingsForm, self).__init__(*args, **kwargs)
        
        choices = [("", "---------")]
        objects = DATA_SETS.world_rooms.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['default_home_key'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['start_location_key'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['default_player_home_key'] = forms.ChoiceField(choices=choices, required=False)

        choices = [("", "---------")]
        objects = DATA_SETS.common_characters.objects.filter(typeclass="CLASS_PLAYER")
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['default_player_character_key'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.game_settings.model
        fields = '__all__'
        list_template = "common_list.html"
        form_template = "common_form.html"


class ClientSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClientSettingsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.client_settings.model
        fields = '__all__'
        list_template = "common_list.html"
        form_template = "common_form.html"


class ClassCategoriesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ClassCategoriesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.class_categories.model
        fields = '__all__'
        desc = 'Categories of classes.'
        list_template = "common_list.html"
        form_template = "common_form.html"


class TypeclassesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TypeclassesForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.class_categories.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['category'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = DATA_SETS.typeclasses.model
        fields = '__all__'


class EquipmentTypesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentTypesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.equipment_types.model
        fields = '__all__'


class EquipmentPositionsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentPositionsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.equipment_positions.model
        fields = '__all__'


class CharacterCareersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterCareersForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.character_careers.model
        fields = '__all__'


class QuestObjectiveTypesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestObjectiveTypesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.quest_objective_types.model
        fields = '__all__'


class EventTypesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventTypesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.event_types.model
        fields = '__all__'


class EventTriggerTypes(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventTriggerTypes, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.event_trigger_types.model
        fields = '__all__'


class QuestDependencyTypesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestDependencyTypesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.quest_dependency_types.model
        fields = '__all__'


class WorldRoomsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(WorldRoomsForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_ROOM")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = DATA_SETS.image_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['background'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.world_rooms.model
        fields = '__all__'


class WorldExitsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(WorldExitsForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_EXIT")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        objects = DATA_SETS.world_rooms.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['location'] = forms.ChoiceField(choices=choices)
        self.fields['destination'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.world_exits.model
        fields = '__all__'


class ExitLocksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExitLocksForm, self).__init__(*args, **kwargs)

        #objects = models.world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.exit_locks.model
        fields = '__all__'


class TwoWayExitsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TwoWayExitsForm, self).__init__(*args, **kwargs)

        #objects = models.world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.two_way_exits.model
        fields = '__all__'


class WorldObjectsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(WorldObjectsForm, self).__init__(*args, **kwargs)

        object = DATA_SETS.typeclasses.objects.get(key="CLASS_WORLD_OBJECT")
        choices = [(object.key, object.name + " (" + object.key + ")")]
        object = DATA_SETS.typeclasses.objects.get(key="CLASS_OBJECT_CREATOR")
        choices.append((object.key, object.name + " (" + object.key + ")"))
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        objects = DATA_SETS.world_rooms.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['location'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.world_objects.model
        fields = '__all__'


class WorldNPCsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(WorldNPCsForm, self).__init__(*args, **kwargs)

        # NPC's typeclass
        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_CHARACTER")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        # NPC's location
        objects = DATA_SETS.world_rooms.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['location'] = forms.ChoiceField(choices=choices)
        
        # NPC's model
        choices = [("", "---------")]
        objects = DATA_SETS.character_models.objects.all()
        model_keys = set([obj.key for obj in objects])
        choices.extend([(model_key, model_key) for model_key in model_keys])
        self.fields['model'] = forms.ChoiceField(choices=choices, required=False)
        
        # NPC's icon
        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.world_npcs.model
        fields = '__all__'


class ObjectCreatorsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ObjectCreatorsForm, self).__init__(*args, **kwargs)

        #objects = models.world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.object_creators.model
        fields = '__all__'


class CreatorLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreatorLootListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        objects = DATA_SETS.world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)
        
        # depends on quest
        choices = [("", "---------")]
        objects = DATA_SETS.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.creator_loot_list.model
        fields = '__all__'


class CharacterLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterLootListForm, self).__init__(*args, **kwargs)

        # providers can be world_npc or common_character
        npcs = DATA_SETS.world_npcs.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in npcs]

        characters = DATA_SETS.common_characters.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in characters])

        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        # depends on quest
        choices = [("", "---------")]
        objects = DATA_SETS.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)
        
    class Meta:
        model = DATA_SETS.character_loot_list.model
        fields = '__all__'


class QuestRewardListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestRewardListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        objects = DATA_SETS.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)
        
        # depends on quest
        choices = [("", "---------")]
        objects = DATA_SETS.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.quest_reward_list.model
        fields = '__all__'


class CommonObjectsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(CommonObjectsForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_OBJECT")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.common_objects.model
        fields = '__all__'


class FoodsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(FoodsForm, self).__init__(*args, **kwargs)
        
        objects = DATA_SETS.typeclasses.objects.filter(key="CLASS_FOOD")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.foods.model
        fields = '__all__'
        

class SkillBooksForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(SkillBooksForm, self).__init__(*args, **kwargs)
        
        objects = DATA_SETS.typeclasses.objects.filter(key="CLASS_SKILL_BOOK")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        # skills
        objects = DATA_SETS.skills.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)
        
        # icons
        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.skill_books.model
        fields = '__all__'
        

class CharacterModelsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterModelsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.character_models.model
        fields = '__all__'


class CommonCharacterForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(CommonCharacterForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_CHARACTER")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        # models
        choices = [("", "---------")]
        objects = DATA_SETS.character_models.objects.all()
        model_keys = set([obj.key for obj in objects])
        choices.extend([(model_key, model_key) for model_key in model_keys])
        self.fields['model'] = forms.ChoiceField(choices=choices, required=False)
        
        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    def clean(self):
        "Validate model and level's value."
        cleaned_data = super(CommonCharacterForm, self).clean()
        if not cleaned_data:
            return

        # check model and level
        model = cleaned_data.get('model')
        level = cleaned_data.get('level')
        try:
            DATA_SETS.character_models.objects.get(key=model, level=level)
        except Exception, e:
            message = "Can not get this level's data."
            levels = DATA_SETS.character_models.objects.filter(key=model)
            available = [str(level.level) for level in levels]
            if len(available) == 1:
                message += " Available level: " + available[0]
            elif len(available) > 1:
                message += " Available levels: " + ", ".join(available)
            self._errors['level'] = self.error_class([message])
            return

        return cleaned_data

    class Meta:
        model = DATA_SETS.common_characters.model
        fields = '__all__'


class DefaultObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultObjectsForm, self).__init__(*args, **kwargs)

        # all character's models
        character_models = set([record.key for record in DATA_SETS.character_models.objects.all()])
        choices = [(key, key) for key in character_models]
        self.fields['character'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = DATA_SETS.default_objects.model
        fields = '__all__'


class ShopsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(ShopsForm, self).__init__(*args, **kwargs)
        
        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_SHOP")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        localize_form_fields(self)
        
    class Meta:
        model = DATA_SETS.shops.model
        fields = '__all__'


class ShopGoodsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(ShopGoodsForm, self).__init__(*args, **kwargs)

        # all shops
        objects = DATA_SETS.shops.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['shop'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        # Goods typeclasses
        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_SHOP_GOODS")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        # available units are common objects
        objects = DATA_SETS.common_objects.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['unit'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = DATA_SETS.shop_goods.model
        fields = '__all__'


class NPCShopsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NPCShopsForm, self).__init__(*args, **kwargs)

        # All NPCs.
        objects = DATA_SETS.world_npcs.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['npc'] = forms.ChoiceField(choices=choices)
        
        # All shops.
        objects = DATA_SETS.shops.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['shop'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = DATA_SETS.npc_shops.model
        fields = '__all__'


class SkillsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(SkillsForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_SKILL")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.skills.model
        fields = '__all__'


class DefaultSkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultSkillsForm, self).__init__(*args, **kwargs)

        # all character's models
        character_models = set([record.key for record in DATA_SETS.character_models.objects.all()])
        choices = [(key, key) for key in character_models]
        self.fields['character'] = forms.ChoiceField(choices=choices)

        objects = DATA_SETS.skills.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = DATA_SETS.default_skills.model
        fields = '__all__'


class NPCDialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NPCDialoguesForm, self).__init__(*args, **kwargs)

        # All NPCs.
        objects = DATA_SETS.world_npcs.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['npc'] = forms.ChoiceField(choices=choices)
        
        objects = DATA_SETS.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.npc_dialogues.model
        fields = '__all__'


class QuestsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(QuestsForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_QUEST")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.quests.model
        fields = '__all__'


class QuestObjectivesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestObjectivesForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)

        objects = DATA_SETS.quest_objective_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.quest_objectives.model
        fields = '__all__'


class QuestDependenciesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestDependenciesForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)
        self.fields['dependency'] = forms.ChoiceField(choices=choices)
        
        objects = DATA_SETS.quest_dependency_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.quest_dependencies.model
        fields = '__all__'


class DialogueQuestDependenciesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueQuestDependenciesForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        
        objects = DATA_SETS.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dependency'] = forms.ChoiceField(choices=choices)
        
        objects = DATA_SETS.quest_dependency_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.dialogue_quest_dependencies.model
        fields = '__all__'


class EquipmentsForm(UniqueKeyForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentsForm, self).__init__(*args, **kwargs)
        
        objects = DATA_SETS.typeclasses.objects.filter(key="CLASS_EQUIPMENT")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        objects = DATA_SETS.equipment_positions.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['position'] = forms.ChoiceField(choices=choices)
        
        objects = DATA_SETS.equipment_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.equipments.model
        fields = '__all__'


class CareerEquipmentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CareerEquipmentsForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.character_careers.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['career'] = forms.ChoiceField(choices=choices)
        
        objects = DATA_SETS.equipment_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['equipment'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.career_equipments.model
        fields = '__all__'


class EventDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDataForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.event_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        objects = DATA_SETS.event_trigger_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['trigger_type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = DATA_SETS.event_data.model
        fields = '__all__'


class EventAttacksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventAttacksForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.event_data.objects.filter(type="EVENT_ATTACK")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['key'] = forms.ChoiceField(choices=choices)
        
        objects = DATA_SETS.common_characters.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['mob'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.event_attacks.model
        fields = '__all__'


class EventDialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDialoguesForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.event_data.objects.filter(type="EVENT_DIALOGUE")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['key'] = forms.ChoiceField(choices=choices)

        objects = DATA_SETS.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        # NPCs
        choices = [("", "---------")]
        objects = DATA_SETS.world_npcs.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['npc'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)
        
    class Meta:
        model = DATA_SETS.event_dialogues.model
        fields = '__all__'


class DialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialoguesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.dialogues.model
        fields = '__all__'


class DialogueRelationsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueRelationsForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        self.fields['next_dlg'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.dialogue_relations.model
        fields = '__all__'


class DialogueSentencesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueSentencesForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        # dialogue's icon
        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        choices = [("", "---------")]
        objects = DATA_SETS.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['provide_quest'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['complete_quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.dialogue_sentences.model
        fields = '__all__'


class LocalizedStringsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LocalizedStringsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.localized_strings.model
        fields = '__all__'


class ResourcesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ResourcesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    def clean(self):
        "Validate values."
        cleaned_data = super(ResourcesForm, self).clean()

        # set object key's default value to the resource name
        key = cleaned_data.get('key')

        if not key:
            key = cleaned_data.get('resource')
            cleaned_data['key'] = key

        if not key:
            message = "This field is needed."
            self._errors['key'] = self.error_class([message])
            return

        return cleaned_data


class ImageResourcesForm(ResourcesForm):
    class Meta:
        model = DATA_SETS.image_resources.model
        fields = ('key', 'name', 'resource',)


class IconResourcesForm(ResourcesForm):
    class Meta:
        model = DATA_SETS.icon_resources.model
        fields = ('key', 'name', 'resource',)
