import sys
from django.contrib.admin.forms import forms
from django.conf import settings
from django.apps import apps
from worlddata import models


def ExistKey(key, except_model=None):
    """
    Check if the key exists.
    """
    # Get models.
    for model_name in settings.OBJECT_DATA_MODELS:
        if model_name == except_model:
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

        classes = models.typeclasses.objects.filter(category="CATE_ROOM")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

    def clean(self):
        "Validate values."
        cleaned_data = super(WorldRoomsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_model=self.Meta.model.__name__):
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

        classes = models.typeclasses.objects.filter(category="CATE_EXIT")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

    def clean(self):
        "Validate values."
        cleaned_data = super(WorldExitsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_model=self.Meta.model.__name__):
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

        locked_exits = models.world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        self.fields['key'] = forms.ModelChoiceField(queryset=locked_exits)

    class Meta:
        model = models.exit_locks
        fields = '__all__'


class WorldObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldObjectsForm, self).__init__(*args, **kwargs)

        classes = models.typeclasses.objects.filter(category="CATE_OBJECT")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

    def clean(self):
        "Validate values."
        cleaned_data = super(WorldObjectsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_model=self.Meta.model.__name__):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        return cleaned_data

    class Meta:
        model = models.world_objects
        fields = '__all__'


class WorldNPCsForm(forms.ModelForm):
    class Meta:
        model = models.world_npcs
        fields = '__all__'


class ObjectCreatorsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ObjectCreatorsForm, self).__init__(*args, **kwargs)

        object_creators = models.world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        self.fields['key'] = forms.ModelChoiceField(queryset=object_creators)

    class Meta:
        model = models.object_creators
        fields = '__all__'


class CreatorLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreatorLootListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        object_creators = models.world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        self.fields['provider'] = forms.ModelChoiceField(queryset=object_creators)

        # available objects are common objects, foods or equipments
        choices = [("", "---------")]

        objects = models.common_objects.objects.all()
        choices.extend([(obj.key, obj.key) for obj in objects])

        foods = models.foods.objects.all()
        choices.extend([(obj.key, obj.key) for obj in foods])

        equipments = models.equipments.objects.all()
        choices.extend([(obj.key, obj.key) for obj in equipments])

        self.fields['object'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.creator_loot_list
        fields = '__all__'


class CharacterLootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterLootListForm, self).__init__(*args, **kwargs)

        # providers can be world_npc or common_character
        choices = [("", "---------")]

        npcs = models.world_npcs.objects.all()
        choices.extend([(obj.key, obj.key) for obj in npcs])

        characters = models.common_characters.objects.all()
        choices.extend([(obj.key, obj.key) for obj in characters])

        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects are common objects, foods or equipments
        choices = [("", "---------")]

        objects = models.common_objects.objects.all()
        choices.extend([(obj.key, obj.key) for obj in objects])

        foods = models.foods.objects.all()
        choices.extend([(obj.key, obj.key) for obj in foods])

        equipments = models.equipments.objects.all()
        choices.extend([(obj.key, obj.key) for obj in equipments])

        self.fields['object'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.character_loot_list
        fields = '__all__'


class QuestRewardListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestRewardListForm, self).__init__(*args, **kwargs)

        # providers must be object_creators
        quests = models.quests.objects.all()
        self.fields['provider'] = forms.ModelChoiceField(queryset=quests)

        # available objects are common objects, foods or equipments
        choices = [("", "---------")]

        objects = models.common_objects.objects.all()
        choices.extend([(obj.key, obj.key) for obj in objects])

        foods = models.foods.objects.all()
        choices.extend([(obj.key, obj.key) for obj in foods])

        equipments = models.equipments.objects.all()
        choices.extend([(obj.key, obj.key) for obj in equipments])

        self.fields['object'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.quest_reward_list
        fields = '__all__'


class CommonObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommonObjectsForm, self).__init__(*args, **kwargs)

        classes = models.typeclasses.objects.filter(category="CATE_OBJECT")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

    def clean(self):
        "Validate values."
        cleaned_data = super(CommonObjectsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_model=self.Meta.model.__name__):
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

        classes = models.typeclasses.objects.filter(category="CATE_CHARACTER")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

        # models
        choices = [("", "---------")]

        model_records = models.character_models.objects.all()
        model_keys = set([obj.key for obj in model_records])
        choices.extend([(model_key, model_key) for model_key in model_keys])

        self.fields['model'] = forms.ChoiceField(choices=choices)

    def clean(self):
        "Validate model and level's value."
        cleaned_data = super(CommonCharacterForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_model=self.Meta.model.__name__):
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

        classes = models.typeclasses.objects.filter(category="CATE_SKILL")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

    def clean(self):
        "Validate values."
        cleaned_data = super(SkillsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_model=self.Meta.model.__name__):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        return cleaned_data

    class Meta:
        model = models.skills
        fields = '__all__'


class DefaultSkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultSkillsForm, self).__init__(*args, **kwargs)

        # all character's models
        choices = [("", "---------")]

        # models
        character_models = set([record.key for record in models.character_models.objects.all()])
        choices.extend([(key, key) for key in character_models])

        # character models
        self.fields['character'] = forms.ChoiceField(choices=choices)

    class Meta:
        model = models.default_skills
        fields = '__all__'


class NPCDialoguesForm(forms.ModelForm):
    class Meta:
        model = models.npc_dialogues
        fields = '__all__'


class QuestsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestsForm, self).__init__(*args, **kwargs)

        classes = models.typeclasses.objects.filter(category="CATE_QUEST")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

    def clean(self):
        "Validate values."
        cleaned_data = super(QuestsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey(key, except_model=self.Meta.model.__name__):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        return cleaned_data

    class Meta:
        model = models.quests
        fields = '__all__'


class QuestObjectivesForm(forms.ModelForm):
    class Meta:
        model = models.quest_objectives
        fields = '__all__'


class QuestDependenciesForm(forms.ModelForm):
    class Meta:
        model = models.quest_dependencies
        fields = '__all__'


class DialogueQuestDependenciesForm(forms.ModelForm):
    class Meta:
        model = models.dialogue_quest_dependencies
        fields = '__all__'


class EquipmentsForm(forms.ModelForm):
    class Meta:
        model = models.equipments
        fields = '__all__'


class CareerEquipmentsForm(forms.ModelForm):
    class Meta:
        model = models.career_equipments
        fields = '__all__'


class EventDataForm(forms.ModelForm):
    class Meta:
        model = models.event_data
        fields = '__all__'


class EventAttacksForm(forms.ModelForm):
    class Meta:
        model = models.event_attacks
        fields = '__all__'


class EventDialoguesForm(forms.ModelForm):
    class Meta:
        model = models.event_dialogues
        fields = '__all__'


class DialoguesForm(forms.ModelForm):
    class Meta:
        model = models.dialogues
        fields = '__all__'


class DialogueRelationsForm(forms.ModelForm):
    class Meta:
        model = models.dialogue_relations
        fields = '__all__'


class DialogueSentencesForm(forms.ModelForm):
    class Meta:
        model = models.dialogue_sentences
        fields = '__all__'


class LocalizedStringsForm(forms.ModelForm):
    class Meta:
        model = models.localized_strings
        fields = '__all__'
