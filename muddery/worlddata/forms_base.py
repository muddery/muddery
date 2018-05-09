
from django.contrib.admin.forms import forms
from muddery.utils.localiztion_handler import localize_form_fields
from muddery.utils.attributes_info_handler import CHARACTER_ATTRIBUTES_INFO, EQUIPMENT_ATTRIBUTES_INFO, FOOD_ATTRIBUTES_INFO
from muddery.mappings.typeclass_set import TYPECLASS_SET
from muddery.worlddata.dao import general_mapper
from muddery.worlddata.dao import model_mapper


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


class EquipmentPositionsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentPositionsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.EQUIPMENT_POSITIONS.model
        fields = '__all__'


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


class WorldNPCsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldNPCsForm, self).__init__(*args, **kwargs)

        # NPC's typeclass
        objects = model_mapper.TYPECLASSES.objects.filter(category="CATE_CHARACTER")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
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


class CreatorLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreatorLootListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        objects = model_mapper.WORLD_OBJECTS.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
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
        model = model_mapper.creator_loot_list.model
        fields = '__all__'


class CharacterLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterLootListForm, self).__init__(*args, **kwargs)

        # providers can be world_npc or common_character
        npcs = model_mapper.world_npcs.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in npcs]

        characters = model_mapper.common_characters.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in characters])

        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        # depends on quest
        choices = [("", "---------")]
        objects = model_mapper.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.character_loot_list.model
        fields = '__all__'


class QuestRewardListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestRewardListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        objects = model_mapper.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)
        
        # depends on quest
        choices = [("", "---------")]
        objects = model_mapper.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.quest_reward_list.model
        fields = '__all__'


class CommonObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommonObjectsForm, self).__init__(*args, **kwargs)

        objects = model_mapper.typeclasses.objects.filter(category="CATE_OBJECT")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = model_mapper.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.common_objects.model
        fields = '__all__'


class FoodsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FoodsForm, self).__init__(*args, **kwargs)
        
        objects = model_mapper.typeclasses.objects.filter(key="CLASS_FOOD")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = model_mapper.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)
        FOOD_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = model_mapper.foods.model
        fields = '__all__'
        

class SkillBooksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SkillBooksForm, self).__init__(*args, **kwargs)
        
        objects = model_mapper.typeclasses.objects.filter(key="CLASS_SKILL_BOOK")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        # skills
        objects = model_mapper.skills.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)
        
        # icons
        choices = [("", "---------")]
        objects = model_mapper.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.skill_books.model
        fields = '__all__'


class CharacterAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True;
        
        localize_form_fields(self)

    class Meta:
        model = model_mapper.character_attributes_info.model
        fields = '__all__'


class EquipmentAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True;
        
        localize_form_fields(self)

    class Meta:
        model = model_mapper.equipment_attributes_info.model
        fields = '__all__'


class FoodAttributesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FoodAttributesForm, self).__init__(*args, **kwargs)
        self.fields['field'].disabled = True;
        
        localize_form_fields(self)

    class Meta:
        model = model_mapper.food_attributes_info.model
        fields = '__all__'


class CharacterModelsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterModelsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)
        CHARACTER_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = model_mapper.character_models.model
        fields = '__all__'


class CommonCharacterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommonCharacterForm, self).__init__(*args, **kwargs)

        objects = model_mapper.typeclasses.objects.filter(category="CATE_CHARACTER")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        # models
        choices = [("", "---------")]
        objects = model_mapper.character_models.objects.all()
        model_keys = set([obj.key for obj in objects])
        choices.extend([(model_key, model_key) for model_key in model_keys])
        self.fields['model'] = forms.ChoiceField(choices=choices, required=False)
        
        choices = [("", "---------")]
        objects = model_mapper.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.common_characters.model
        fields = '__all__'


class DefaultObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultObjectsForm, self).__init__(*args, **kwargs)

        # all character's models
        character_models = set([record.key for record in model_mapper.character_models.objects.all()])
        choices = [(key, key) for key in character_models]
        self.fields['character'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.default_objects.model
        fields = '__all__'


class ShopsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShopsForm, self).__init__(*args, **kwargs)
        
        objects = model_mapper.typeclasses.objects.filter(category="CATE_SHOP")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = model_mapper.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.shops.model
        fields = '__all__'


class ShopGoodsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShopGoodsForm, self).__init__(*args, **kwargs)

        # all shops
        objects = model_mapper.shops.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['shop'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        # Goods typeclasses
        objects = model_mapper.typeclasses.objects.filter(category="CATE_SHOP_GOODS")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        # available units are common objects
        objects = model_mapper.common_objects.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['unit'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.shop_goods.model
        fields = '__all__'


class NPCShopsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NPCShopsForm, self).__init__(*args, **kwargs)

        # All NPCs.
        objects = model_mapper.world_npcs.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['npc'] = forms.ChoiceField(choices=choices)
        
        # All shops.
        objects = model_mapper.shops.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['shop'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.npc_shops.model
        fields = '__all__'


class SkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SkillsForm, self).__init__(*args, **kwargs)

        objects = model_mapper.typeclasses.objects.filter(category="CATE_SKILL")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = model_mapper.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        choices = [("", "---------")]
        objects = model_mapper.skill_types.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['main_type'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['sub_type'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.skills.model
        fields = '__all__'
        
        
class SkillTypesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SkillTypesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.skill_types.model
        fields = '__all__'


class DefaultSkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultSkillsForm, self).__init__(*args, **kwargs)

        # all character's models
        character_models = set([record.key for record in model_mapper.character_models.objects.all()])
        choices = [(key, key) for key in character_models]
        self.fields['character'] = forms.ChoiceField(choices=choices)

        objects = model_mapper.skills.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.default_skills.model
        fields = '__all__'


class NPCDialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NPCDialoguesForm, self).__init__(*args, **kwargs)

        # All NPCs.
        objects = model_mapper.world_npcs.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['npc'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.npc_dialogues.model
        fields = '__all__'


class QuestsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestsForm, self).__init__(*args, **kwargs)

        objects = model_mapper.typeclasses.objects.filter(category="CATE_QUEST")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.quests.model
        fields = '__all__'


class QuestObjectivesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestObjectivesForm, self).__init__(*args, **kwargs)

        objects = model_mapper.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)

        objects = model_mapper.quest_objective_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.quest_objectives.model
        fields = '__all__'


class QuestDependenciesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestDependenciesForm, self).__init__(*args, **kwargs)

        objects = model_mapper.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)
        self.fields['dependency'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.quest_dependency_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.quest_dependencies.model
        fields = '__all__'


class DialogueQuestDependenciesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueQuestDependenciesForm, self).__init__(*args, **kwargs)

        objects = model_mapper.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dependency'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.quest_dependency_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.dialogue_quest_dependencies.model
        fields = '__all__'


class EquipmentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentsForm, self).__init__(*args, **kwargs)
        
        objects = model_mapper.typeclasses.objects.filter(key="CLASS_EQUIPMENT")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        objects = model_mapper.equipment_positions.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['position'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.equipment_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = model_mapper.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        localize_form_fields(self)
        EQUIPMENT_ATTRIBUTES_INFO.set_form_fields(self)

    class Meta:
        model = model_mapper.equipments.model
        fields = '__all__'


class CareerEquipmentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CareerEquipmentsForm, self).__init__(*args, **kwargs)

        objects = model_mapper.character_careers.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['career'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.equipment_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['equipment'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.career_equipments.model
        fields = '__all__'


class EventDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDataForm, self).__init__(*args, **kwargs)

        objects = model_mapper.event_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        objects = model_mapper.event_trigger_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['trigger_type'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.event_data.model
        fields = '__all__'


class EventAttacksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventAttacksForm, self).__init__(*args, **kwargs)

        objects = model_mapper.event_data.objects.filter(type="EVENT_ATTACK")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['key'] = forms.ChoiceField(choices=choices)
        
        objects = model_mapper.common_characters.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['mob'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.event_attacks.model
        fields = '__all__'


class EventDialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDialoguesForm, self).__init__(*args, **kwargs)

        objects = model_mapper.event_data.objects.filter(type="EVENT_DIALOGUE")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['key'] = forms.ChoiceField(choices=choices)

        objects = model_mapper.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        # NPCs
        choices = [("", "---------")]
        objects = model_mapper.world_npcs.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['npc'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)
        
    class Meta:
        model = model_mapper.event_dialogues.model
        fields = '__all__'


class DialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialoguesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.dialogues.model
        fields = '__all__'


class DialogueRelationsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueRelationsForm, self).__init__(*args, **kwargs)

        objects = model_mapper.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        self.fields['next_dlg'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.dialogue_relations.model
        fields = '__all__'


class DialogueSentencesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueSentencesForm, self).__init__(*args, **kwargs)

        objects = model_mapper.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

        # dialogue's icon
        choices = [("", "---------")]
        objects = model_mapper.icon_resources.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['icon'] = forms.ChoiceField(choices=choices, required=False)
        
        choices = [("", "---------")]
        objects = model_mapper.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['provide_quest'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['complete_quest'] = forms.ChoiceField(choices=choices, required=False)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.dialogue_sentences.model
        fields = '__all__'


class ConditionDescForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConditionDescForm, self).__init__(*args, **kwargs)

        choices = get_all_objects()
        self.fields['key'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = model_mapper.condition_desc.model
        fields = '__all__'
        

class LocalizedStringsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LocalizedStringsForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = common_mapper.get_model("localized_strings")
        fields = '__all__'


class ImageResourcesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImageResourcesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.image_resources.model
        fields = ('key', 'name', 'resource',)


class IconResourcesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(IconResourcesForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = model_mapper.icon_resources.model
        fields = ('key', 'name', 'resource',)
