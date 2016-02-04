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


class ExitLocksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExitLocksForm, self).__init__(*args, **kwargs)

        locked_exits = models.world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        self.fields['key'] = forms.ModelChoiceField(queryset=locked_exits)


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


class ObjectCreatorsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ObjectCreatorsForm, self).__init__(*args, **kwargs)

        object_creators = models.world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        self.fields['key'] = forms.ModelChoiceField(queryset=object_creators)


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


class CharacterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterForm, self).__init__(*args, **kwargs)

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
        cleaned_data = super(CharacterForm, self).clean()

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