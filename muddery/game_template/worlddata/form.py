from django.contrib.admin.forms import forms
from worlddata.models import *


#
# Field
#


class SkillsModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.key


class DialogueModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.key


class QuestModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.key


class NPCModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.key


class WorldObjectModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.key


#
# Form
#


class WorldExitsForm(forms.ModelForm):
    ROOMS_LIST_CHOICES = []

    def __init__(self, *args, **kwargs):
        super(WorldExitsForm, self).__init__(*args, **kwargs)
        if self.instance.key:
            rooms_list = world_rooms.objects.all()
            for room_obj in rooms_list:
                self.ROOMS_LIST_CHOICES.append((room_obj.key, room_obj.key))
            self.fields['location'] = forms.ChoiceField(
                choices=self.ROOMS_LIST_CHOICES)
            self.fields['destination'] = forms.ChoiceField(
                choices=self.ROOMS_LIST_CHOICES)


class WorldObjectForm(forms.ModelForm):
    ROOMS_LIST_CHOICES = []

    def __init__(self, *args, **kwargs):
        super(WorldObjectForm, self).__init__(*args, **kwargs)
        if self.instance.key:
            rooms_list = world_rooms.objects.all()
            for room_obj in rooms_list:
                self.ROOMS_LIST_CHOICES.append((room_obj.key, room_obj.key))
            self.fields['location'] = forms.ChoiceField(
                choices=self.ROOMS_LIST_CHOICES)


class WorldNPCForm(forms.ModelForm):
    ROOMS_LIST_CHOICES = []
    MODELS_LIST_CHOICES = []

    def __init__(self, *args, **kwargs):
        super(WorldNPCForm, self).__init__(*args, **kwargs)
        if self.instance.key:
            rooms_list = world_rooms.objects.all()
            for room_obj in rooms_list:
                self.ROOMS_LIST_CHOICES.append((room_obj.key, room_obj.key))
            self.fields['location'] = forms.ChoiceField(
                choices=self.ROOMS_LIST_CHOICES)

            models_list = common_characters.objects.all()
            for model_obj in models_list:
                self.MODELS_LIST_CHOICES.append((model_obj.key, model_obj.key))
            self.fields['model'] = forms.ChoiceField(
                choices=self.MODELS_LIST_CHOICES)


class CommonCharactersForm(forms.ModelForm):
    ROOMS_LIST_CHOICES = []
    MODELS_LIST_CHOICES = []

    def __init__(self, *args, **kwargs):
        super(CommonCharactersForm, self).__init__(*args, **kwargs)
        if self.instance.key:
            models_list = common_characters.objects.all()
            for model_obj in models_list:
                self.MODELS_LIST_CHOICES.append((model_obj.key, model_obj.key))
            self.fields['model'] = forms.ChoiceField(
                choices=self.MODELS_LIST_CHOICES)


class CharacterSkillsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CharacterSkillsForm, self).__init__(*args, **kwargs)
        if self.instance.character:
            self.fields['skill'] = SkillsModelChoiceField(queryset=skills.objects.all())


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


class ExitLocksForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExitLocksForm, self).__init__(*args, **kwargs)

        locked_exits = world_exits.objects.filter(typeclass="CLASS_LOCKED_EXIT")
        self.fields['key'] = forms.ModelChoiceField(queryset=locked_exits)


class ObjectCreatorsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ObjectCreatorsForm, self).__init__(*args, **kwargs)

        object_creators = world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        self.fields['key'] = forms.ModelChoiceField(queryset=object_creators)


class LootListForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LootListForm, self).__init__(*args, **kwargs)

        choices = [("", "---------")]

        object_creators = world_objects.objects.filter(typeclass="CLASS_OBJECT_CREATOR")
        choices.extend([(obj.key, obj.key) for obj in object_creators])

        npcs = world_npcs.objects.all()
        choices.extend([(obj.key, obj.key) for obj in npcs])

        characters = common_characters.objects.all()
        choices.extend([(obj.key, obj.key) for obj in characters])

        self.fields['provider'] = forms.ChoiceField(choices=choices)

        objects = common_objects.objects.all()
        self.fields['object'] = forms.ModelChoiceField(queryset=objects)

        quests = world_objects.objects.filter(typeclass="CLASS_QUEST")
        self.fields['quest'] = forms.ModelChoiceField(queryset=quests)


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