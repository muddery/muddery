from django.contrib.admin.forms import forms
from django.conf import settings
from django.apps import apps
from worlddata.models import *

#
# Form
#


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
            model_obj.objects.get(key=model_name)
            return True
        except Exception, e:
            continue

    return False


class WorldRoomsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldRoomsForm, self).__init__(*args, **kwargs)

        classes = typeclasses.objects.filter(category="CATE_ROOM")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

    def clean(self):
        "Validate values."
        cleaned_data = super(WorldRoomsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if ExistKey.ExistKey(key, except_model=self._mega.model):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        return cleaned_data


class WorldExitsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldExitsForm, self).__init__(*args, **kwargs)

        classes = typeclasses.objects.filter(category="CATE_EXIT")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

    def clean(self):
        "Validate values."
        cleaned_data = super(WorldExitsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if OBJECT_KEY_HANDLER.has_key(key):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        return cleaned_data


class ExitLocksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExitLocksForm, self).__init__(*args, **kwargs)

        locked_exits = world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        self.fields['key'] = forms.ModelChoiceField(queryset=locked_exits)


class WorldObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorldObjectsForm, self).__init__(*args, **kwargs)

        classes = typeclasses.objects.filter(category="CATE_OBJECT")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

    def clean(self):
        "Validate values."
        cleaned_data = super(WorldObjectsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if OBJECT_KEY_HANDLER.has_key(key):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return


class ObjectCreatorsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ObjectCreatorsForm, self).__init__(*args, **kwargs)

        object_creators = world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        self.fields['key'] = forms.ModelChoiceField(queryset=object_creators)


class LootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LootListForm, self).__init__(*args, **kwargs)

        # providers
        choices = [("", "---------")]

        object_creators = world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        choices.extend([(obj.key, obj.key) for obj in object_creators])

        npcs = world_npcs.objects.all()
        choices.extend([(obj.key, obj.key) for obj in npcs])

        characters = common_characters.objects.all()
        choices.extend([(obj.key, obj.key) for obj in characters])

        self.fields['provider'] = forms.ChoiceField(choices=choices)

        # available objects
        choices = [("", "---------")]

        objects = common_objects.objects.all()
        choices.extend([(obj.key, obj.key) for obj in objects])

        self.fields['object'] = forms.ModelChoiceField(queryset=objects)


class CommonObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommonObjectsForm, self).__init__(*args, **kwargs)

        classes = typeclasses.objects.filter(category="CATE_OBJECT")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

    def clean(self):
        "Validate values."
        cleaned_data = super(CommonObjectsForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if OBJECT_KEY_HANDLER.has_key(key):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return


class CharacterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterForm, self).__init__(*args, **kwargs)

        classes = typeclasses.objects.filter(category="CATE_CHARACTER")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)

        # models
        choices = [("", "---------")]

        models = character_models.objects.all()
        models = set([obj.key for obj in models])
        choices.extend([(model, model) for model in models])

        self.fields['model'] = forms.ChoiceField(choices=choices)

    def clean(self):
        "Validate model and level's value."
        cleaned_data = super(CharacterForm, self).clean()

        # object's key should be unique
        key = cleaned_data.get('key')
        if OBJECT_KEY_HANDLER.has_key(key):
            message = "This key has been used. Please use another one."
            self._errors['key'] = self.error_class([message])
            return

        # check model and level
        model = cleaned_data.get('model')
        level = cleaned_data.get('level')
        try:
            character_models.objects.get(key=model, level=level)
        except Exception, e:
            message = "Can not get this level's data."
            levels = character_models.objects.filter(key=model)
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

        classes = typeclasses.objects.filter(category="CATE_SKILL")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)


class DefaultSkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DefaultSkillsForm, self).__init__(*args, **kwargs)

        # all characters
        choices = [("", "---------")]

        npcs = world_npcs.objects.all()
        choices.extend([(obj.key, obj.key) for obj in npcs])

        characters = common_characters.objects.all()
        choices.extend([(obj.key, obj.key) for obj in characters])

        self.fields['character'] = forms.ChoiceField(choices=choices)


class QuestsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestsForm, self).__init__(*args, **kwargs)

        classes = typeclasses.objects.filter(category="CATE_QUEST")
        self.fields['typeclass'] = forms.ModelChoiceField(queryset=classes)


class DialogueQuestDependencyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueQuestDependencyForm, self).__init__(*args, **kwargs)
        if self.instance.dialogue:
            self.fields['dialogue'] = DialogueModelChoiceField(queryset=dialogues.objects.all())
            self.fields['dependency'] = QuestModelChoiceField(queryset=quests.objects.all())


class DialogueRelationsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueRelationsForm, self).__init__(*args, **kwargs)
        if self.instance.dialogue:
            self.fields['dialogue'] = DialogueModelChoiceField(queryset=dialogues.objects.all())
            self.fields['next'] = DialogueModelChoiceField(queryset=quests.objects.all())


class DialogueSentencesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialogueSentencesForm, self).__init__(*args, **kwargs)
        if self.instance.dialogue:
            self.fields['dialogue'] = DialogueModelChoiceField(queryset=dialogues.objects.all())
            self.fields['provide_quest'] = QuestModelChoiceField(queryset=quests.objects.all())
            self.fields['complete_quest'] = QuestModelChoiceField(queryset=quests.objects.all())


class DialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DialoguesForm, self).__init__(*args, **kwargs)
        if self.instance.key:
            self.fields['have_quest'] = QuestModelChoiceField(queryset=quests.objects.all())


class EventDialoguesForm(forms.ModelForm):
    DIALOGUE_LIST_CHOICES = []
    NPC_LIST_CHOICES = []

    def __init__(self, *args, **kwargs):
        super(EventDialoguesForm, self).__init__(*args, **kwargs)
        if self.instance.key:
            dialogue_list = dialogues.objects.all()
            for dialogue_obj in dialogue_list:
                self.DIALOGUE_LIST_CHOICES.append((dialogue_obj.key, dialogue_obj.key))
            self.fields['dialogue'] = forms.ChoiceField(
                choices=self.DIALOGUE_LIST_CHOICES)
            npc_list = world_npcs.objects.all()
            for npc_obj in npc_list:
                self.NPC_LIST_CHOICES.append((npc_obj.key, npc_obj.key))
            self.fields['npc'] = forms.ChoiceField(
                choices=self.NPC_LIST_CHOICES)


class NPCDialoguesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NPCDialoguesForm, self).__init__(*args, **kwargs)
        if self.instance.npc:
            self.fields['npc'] = NPCModelChoiceField(queryset=world_npcs.objects.all())
            self.fields['dialogue'] = DialogueModelChoiceField(queryset=dialogues.objects.all())


class QuestObjectivesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestObjectivesForm, self).__init__(*args, **kwargs)
        if self.instance.quest:
            self.fields['quest'] = QuestModelChoiceField(queryset=quests.objects.all())


class QuestDependencyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestDependencyForm, self).__init__(*args, **kwargs)
        if self.instance.quest:
            self.fields['quest'] = QuestModelChoiceField(queryset=quests.objects.all())
            self.fields['dependency'] = QuestModelChoiceField(queryset=quests.objects.all())