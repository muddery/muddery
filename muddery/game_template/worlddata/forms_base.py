import sys
from django.contrib.admin.forms import forms
from django.conf import settings
from django.apps import apps
from worlddata import models


def ExistKey(key, except_models=None):
    """
    Check if the key exists.
    """
    # Get models.
    for model_name in settings.OBJECT_DATA_MODELS:
        if model_name in except_models:
            continue
        try:
            model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
            model_obj.objects.get(key=key)
            return True
        except Exception, e:
            continue

    return False


class GameSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GameSettingsForm, self).__init__(*args, **kwargs)
        
        choices = [("", "---------")]
        objects = models.world_rooms.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['default_home_key'] = forms.ChoiceField(choices=choices)
        self.fields['start_location_key'] = forms.ChoiceField(choices=choices)
        self.fields['default_player_home_key'] = forms.ChoiceField(choices=choices)

        choices = [("", "---------")]
        objects = models.character_models.objects.filter(level=1)
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['default_player_model_key'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.game_settings
        fields = '__all__'
        list_template = "common_list.html"
        form_template = "common_form.html"


class ClientSettingsForm(forms.ModelForm):
    class Meta:
        model = models.client_settings
        fields = '__all__'
        list_template = "common_list.html"
        form_template = "common_form.html"


class ClassCategoriesForm(forms.ModelForm):
    class Meta:
        model = models.class_categories
        fields = '__all__'
        desc = 'Categories of classes.'
        list_template = "common_list.html"
        form_template = "common_form.html"


class TypeclassesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TypeclassesForm, self).__init__(*args, **kwargs)

        objects = models.class_categories.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['category'] = forms.ChoiceField(choices=choices)
        
    class Meta:
        model = models.typeclasses
        fields = '__all__'


class EquipmentTypesForm(forms.ModelForm):
    class Meta:
        model = models.equipment_types
        fields = '__all__'


class EquipmentPositionsForm(forms.ModelForm):
    class Meta:
        model = models.equipment_positions
        fields = '__all__'


class CharacterCareersForm(forms.ModelForm):
    class Meta:
        model = models.character_careers
        fields = '__all__'


class QuestObjectiveTypesForm(forms.ModelForm):
    class Meta:
        model = models.quest_objective_types
        fields = '__all__'


class EventTypesForm(forms.ModelForm):
    class Meta:
        model = models.event_types
        fields = '__all__'


class EventTriggerTypes(forms.ModelForm):
    class Meta:
        model = models.event_trigger_types
        fields = '__all__'


class QuestDependencyTypesForm(forms.ModelForm):
    class Meta:
        model = models.quest_dependency_types
        fields = '__all__'


class WorldRoomsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldRoomsForm, self).__init__(*args, **kwargs)

        objects = models.typeclasses.objects.filter(category="CATE_ROOM")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

    def clean(self):
        "Validate values."
        cleaned_data = super(WorldRoomsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_models=[self.Meta.model.__name__]):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        return cleaned_data

    class Meta:
        model = models.world_rooms
        fields = '__all__'


class WorldExitsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldExitsForm, self).__init__(*args, **kwargs)

        objects = models.typeclasses.objects.filter(category="CATE_EXIT")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        objects = models.world_rooms.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['location'] = forms.ChoiceField(choices=choices)
        self.fields['destination'] = forms.ChoiceField(choices=choices)

    def clean(self):
        "Validate values."
        cleaned_data = super(WorldExitsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_models=[self.Meta.model.__name__]):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        return cleaned_data

    class Meta:
        model = models.world_exits
        fields = '__all__'


class ExitLocksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExitLocksForm, self).__init__(*args, **kwargs)

        #objects = models.world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.exit_locks
        fields = '__all__'


class WorldObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldObjectsForm, self).__init__(*args, **kwargs)

        object = models.typeclasses.objects.get(key="CLASS_WORLD_OBJECT")
        choices = [(object.key, object.name + " (" + object.key + ")")]
        object = models.typeclasses.objects.get(key="CLASS_OBJECT_CREATOR")
        choices.append((object.key, object.name + " (" + object.key + ")"))
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        objects = models.world_rooms.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['location'] = forms.ChoiceField(choices=choices)

    def clean(self):
        "Validate values."
        cleaned_data = super(WorldObjectsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_models=[self.Meta.model.__name__]):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        return cleaned_data

    class Meta:
        model = models.world_objects
        fields = '__all__'


class WorldNPCsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldNPCsForm, self).__init__(*args, **kwargs)

        objects = models.typeclasses.objects.filter(category="CATE_CHARACTER")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)
        
        objects = models.world_rooms.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['location'] = forms.ChoiceField(choices=choices)
        
    class Meta:
        model = models.world_npcs
        fields = '__all__'


class ObjectCreatorsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ObjectCreatorsForm, self).__init__(*args, **kwargs)

        #objects = models.world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        #choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        #self.fields['key'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.object_creators
        fields = '__all__'


class CreatorLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreatorLootListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        objects = models.world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects are common objects, foods or equipments
        objects = models.common_objects.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]

        foods = models.foods.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in foods])

        equipments = models.equipments.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in equipments])

        self.fields['object'] = forms.ChoiceField(choices=choices)
        
        # depends on quest
        choices = [("", "---------")]
        objects = models.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices)
        self.fields['quest'].label = u"Depends on quest"

    class Meta:
        model = models.creator_loot_list
        fields = '__all__'


class CharacterLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterLootListForm, self).__init__(*args, **kwargs)

        # providers can be world_npc or common_character
        npcs = models.world_npcs.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in npcs]

        characters = models.common_characters.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in characters])

        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects are common objects, foods or equipments
        objects = models.common_objects.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]

        foods = models.foods.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in foods])

        equipments = models.equipments.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in equipments])

        self.fields['object'] = forms.ChoiceField(choices=choices)

        # depends on quest
        choices = [("", "---------")]
        objects = models.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices)
        self.fields['quest'].label = u"Depends on quest"
        
    class Meta:
        model = models.character_loot_list
        fields = '__all__'


class QuestRewardListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestRewardListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        objects = models.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects are common objects, foods or equipments
        objects = models.common_objects.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]

        foods = models.foods.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in foods])

        equipments = models.equipments.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in equipments])

        self.fields['object'] = forms.ChoiceField(choices=choices)
        
        # depends on quest
        choices = [("", "---------")]
        objects = models.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['quest'] = forms.ChoiceField(choices=choices)
        self.fields['quest'].label = u"Depends on quest"

    class Meta:
        model = models.quest_reward_list
        fields = '__all__'


class CommonObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommonObjectsForm, self).__init__(*args, **kwargs)

        objects = models.typeclasses.objects.filter(category="CATE_OBJECT")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

    def clean(self):
        "Validate values."
        cleaned_data = super(CommonObjectsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_models=[self.Meta.model.__name__]):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        return cleaned_data

    class Meta:
        model = models.common_objects
        fields = '__all__'


class CharacterModelsForm(forms.ModelForm):
    class Meta:
        model = models.character_models
        fields = '__all__'


class CommonCharacterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommonCharacterForm, self).__init__(*args, **kwargs)

        objects = models.typeclasses.objects.filter(category="CATE_CHARACTER")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        # models
        choices = [("", "---------")]
        objects = models.character_models.objects.all()
        model_keys = set([obj.key for obj in objects])
        choices.extend([(model_key, model_key) for model_key in model_keys])
        self.fields['model'] = forms.ChoiceField(choices=choices)

    def clean(self):
        "Validate model and level's value."
        cleaned_data = super(CommonCharacterForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_models=[self.Meta.model.__name__]):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        # check model and level
        model = cleaned_data.get('model')
        level = cleaned_data.get('level')
        try:
            models.character_models.objects.get(key=model, level=level)
        except Exception, e:
            message = "Can not get this level's data."
            levels = models.character_models.objects.filter(key=model)
            available = [str(level.level) for level in levels]
            if len(available) == 1:
                message += " Available level: " + available[0]
            elif len(available) > 1:
                message += " Available levels: " + ", ".join(available)
            self._errors['level'] = self.error_class([message])
            return

        return cleaned_data

    class Meta:
        model = models.common_characters
        fields = '__all__'


class SkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SkillsForm, self).__init__(*args, **kwargs)

        objects = models.typeclasses.objects.filter(category="CATE_SKILL")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.skills
        fields = '__all__'


class DefaultSkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultSkillsForm, self).__init__(*args, **kwargs)

        # all character's models
        character_models = set([record.key for record in models.character_models.objects.all()])
        choices = [(key, key) for key in character_models]
        self.fields['character'] = forms.ChoiceField(choices=choices)

        objects = models.skills.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)
        
    class Meta:
        model = models.default_skills
        fields = '__all__'


class NPCDialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NPCDialoguesForm, self).__init__(*args, **kwargs)

        objects = models.world_npcs.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['npc'] = forms.ChoiceField(choices=choices)
        
        objects = models.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.npc_dialogues
        fields = '__all__'


class QuestsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestsForm, self).__init__(*args, **kwargs)

        objects = models.typeclasses.objects.filter(category="CATE_QUEST")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.quests
        fields = '__all__'


class QuestObjectivesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestObjectivesForm, self).__init__(*args, **kwargs)

        objects = models.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)

        objects = models.quest_objective_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.quest_objectives
        fields = '__all__'


class QuestDependenciesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestDependenciesForm, self).__init__(*args, **kwargs)

        objects = models.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)
        self.fields['dependency'] = forms.ChoiceField(choices=choices)
        
        objects = models.quest_dependency_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.quest_dependencies
        fields = '__all__'


class DialogueQuestDependenciesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueQuestDependenciesForm, self).__init__(*args, **kwargs)

        objects = models.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        
        objects = models.quests.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dependency'] = forms.ChoiceField(choices=choices)
        
        objects = models.quest_dependency_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.dialogue_quest_dependencies
        fields = '__all__'


class EquipmentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentsForm, self).__init__(*args, **kwargs)
        
        objects = models.typeclasses.objects.filter(category="CATE_OBJECT")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['typeclass'] = forms.ChoiceField(choices=choices)

        objects = models.equipment_positions.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['position'] = forms.ChoiceField(choices=choices)
        
        objects = models.equipment_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.equipments
        fields = '__all__'


class CareerEquipmentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CareerEquipmentsForm, self).__init__(*args, **kwargs)

        objects = models.character_careers.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['career'] = forms.ChoiceField(choices=choices)
        
        objects = models.equipment_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['equipment'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.career_equipments
        fields = '__all__'


class EventDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDataForm, self).__init__(*args, **kwargs)

        objects = models.event_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['type'] = forms.ChoiceField(choices=choices)

        objects = models.event_trigger_types.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['trigger_type'] = forms.ChoiceField(choices=choices)
        
    class Meta:
        model = models.event_data
        fields = '__all__'


class EventAttacksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventAttacksForm, self).__init__(*args, **kwargs)

        objects = models.event_data.objects.filter(type="EVENT_ATTACK")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['key'] = forms.ChoiceField(choices=choices)
        
        objects = models.common_characters.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['mob'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.event_attacks
        fields = '__all__'


class EventDialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDialoguesForm, self).__init__(*args, **kwargs)

        objects = models.event_data.objects.filter(type="EVENT_DIALOGUE")
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['key'] = forms.ChoiceField(choices=choices)

        objects = models.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        
        objects = models.world_npcs.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['npc'] = forms.ChoiceField(choices=choices)
        
    class Meta:
        model = models.event_dialogues
        fields = '__all__'


class DialoguesForm(forms.ModelForm):
    class Meta:
        model = models.dialogues
        fields = '__all__'


class DialogueRelationsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueRelationsForm, self).__init__(*args, **kwargs)

        objects = models.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        self.fields['next'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.dialogue_relations
        fields = '__all__'


class DialogueSentencesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueSentencesForm, self).__init__(*args, **kwargs)

        objects = models.dialogues.objects.all()
        choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
        self.fields['dialogue'] = forms.ChoiceField(choices=choices)
        
        choices = [("", "---------")]
        objects = models.quests.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['provide_quest'] = forms.ChoiceField(choices=choices)
        self.fields['complete_quest'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.dialogue_sentences
        fields = '__all__'


class LocalizedStringsForm(forms.ModelForm):
    class Meta:
        model = models.localized_strings
        fields = '__all__'
