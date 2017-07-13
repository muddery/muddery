
from django.contrib.admin.forms import forms
from muddery.utils.localiztion_handler import localize_form_fields
from muddery.utils.attributes_info_handler import CHARACTER_ATTRIBUTES_INFO, EQUIPMENT_ATTRIBUTES_INFO, FOOD_ATTRIBUTES_INFO
from muddery.worlddata.data_sets import DATA_SETS


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


class WorldAreasForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldAreasForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_AREA")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = DATA_SETS.image_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['background'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.world_areas.model
        fields = '__all__'
        
    
class WorldRoomsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldRoomsForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.typeclasses.objects.filter(category="CATE_ROOM")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = DATA_SETS.world_areas.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['location'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = DATA_SETS.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        choices = [("", "---------")]
        objects = DATA_SETS.image_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['background'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.world_rooms.model
        fields = '__all__'


class WorldExitsForm(forms.ModelForm):
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


class WorldObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldObjectsForm, self).__init__(*args, **kwargs)

        objects = DATA_SETS.typeclasses.objects.get(key="CLASS_WORLD_OBJECT")
        choices = [(objects.key, objects.name + " (" + objects.key + ")")]
        objects = DATA_SETS.typeclasses.objects.get(key="CLASS_OBJECT_CREATOR")
        choices.append((objects.key, objects.name + " (" + objects.key + ")"))
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


class WorldNPCsForm(forms.ModelForm):
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


class CommonObjectsForm(forms.ModelForm):
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


class FoodsForm(forms.ModelForm):
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
        FOOD_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = DATA_SETS.foods.model
        fields = '__all__'
        

class SkillBooksForm(forms.ModelForm):
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


class CharacterAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True;
        
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.character_attributes_info.model
        fields = '__all__'


class EquipmentAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True;
        
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.equipment_attributes_info.model
        fields = '__all__'


class FoodAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FoodAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True;
        
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.food_attributes_info.model
        fields = '__all__'


class CharacterModelsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterModelsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)
        CHARACTER_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = DATA_SETS.character_models.model
        fields = '__all__'


class CommonCharacterForm(forms.ModelForm):
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


class ShopsForm(forms.ModelForm):
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


class ShopGoodsForm(forms.ModelForm):
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


class SkillsForm(forms.ModelForm):
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


class QuestsForm(forms.ModelForm):
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


class EquipmentsForm(forms.ModelForm):
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
        EQUIPMENT_ATTRIBUTES_INFO.set_form_fields(self)

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


class ImageResourcesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImageResourcesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.image_resources.model
        fields = ('key', 'name', 'resource',)


class IconResourcesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(IconResourcesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = DATA_SETS.icon_resources.model
        fields = ('key', 'name', 'resource',)
