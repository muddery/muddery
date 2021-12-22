
from wtforms import Form, validators, widgets
from wtforms.fields import SelectField
from django import forms
from muddery.server.utils.localiztion_handler import localize_form_fields
from muddery.server.mappings.quest_objective_set import QUEST_OBJECTIVE_SET
from muddery.server.mappings.quest_status_set import QUEST_STATUS_SET
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.server.mappings.event_trigger_set import EVENT_TRIGGER_SET
from muddery.worldeditor.dao import common_mappers as CM
from muddery.worldeditor.dao.general_query_mapper import get_element_base_data
from muddery.worldeditor.forms.location_field import LocationField
from muddery.worldeditor.forms.image_field import ImageField
from muddery.worldeditor.forms.create_form import create_form


def get_all_pocketable_objects():
    """
    Get all objects that can be put in player's pockets.
    """
    records = CM.COMMON_OBJECTS.all_with_base()
    return [(r["key"], r["name"] + " (" + r["key"] + ")") for r in records]


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
        except Exception as e:
            pass

    return form_obj.instance.__class__.__name__ + "_" + str(index)


class GameSettingsForm(create_form("game_settings")):
    choices = [("", "---------")]
    records = get_element_base_data("ROOM")
    choices.extend([(record.key, record.name + " (" + record.key + ")") for record in records])
    start_location_key = SelectField(choices=choices)
    default_player_home_key = SelectField(choices=choices)

    choices = [("", "---------")]
    records = get_element_base_data("PLAYER_CHARACTER")
    choices.extend([(record.key, record.name + " (" + record.key + ")") for record in records])
    default_player_character_key = SelectField(choices=choices)

    choices = [("", "---------")]
    records = get_element_base_data("STAFF_CHARACTER")
    choices.extend([(record.key, record.name + " (" + record.key + ")") for record in records])
    default_staff_character_key = SelectField(choices=choices)


class HonourSettingsForm(create_form("honour_settings")):
    pass


class EquipmentTypesForm(create_form("equipment_types")):
    pass


class EquipmentPositionsForm(create_form("equipment_positions")):
    pass


class WorldAreasForm(create_form("world_areas")):
    background = ImageField(image_type="background")


class WorldRoomsForm(create_form("world_rooms")):
    choices = [("", "---------")]
    objects = CM.WORLD_AREAS.all_with_base()
    choices.extend([(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects])
    area = SelectField(choices=choices)

    icon = ImageField(image_type="icon")

    background = ImageField(image_type="background")


class WorldExitsForm(create_form("world_exits")):
    rooms = CM.WORLD_ROOMS.all_with_base()
    choices = [(r["key"], r["name"] + " (" + r["key"] + ")") for r in rooms]
    location = LocationField(choices=choices)
    destination = LocationField(choices=choices)


class WorldObjectsForm(create_form("world_objects")):
    rooms = CM.WORLD_ROOMS.all_with_base()
    choices = [(r["key"], r["name"] + " (" + r["key"] + ")") for r in rooms]
    location = LocationField(choices=choices)

    icon = ImageField(image_type="icon")


class WorldNPCsForm(create_form("world_npcs")):
    # NPC's location
    rooms = CM.WORLD_ROOMS.all_with_base()
    choices = [(r["key"], r["name"] + " (" + r["key"] + ")") for r in rooms]
    location = LocationField(choices=choices)


class ObjectCreatorsForm(create_form("object_creator")):
    pass


class CreatorLootListForm(create_form("creator_loot_list")):
    # providers must be object_creators
    objects = CM.OBJECT_CREATORS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    provider = forms.ChoiceField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = forms.ChoiceField(choices=choices)

    # depends on quest
    choices = [("", "---------")]
    objects = CM.QUESTS.all_with_base()
    choices.extend([(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects])
    quest = forms.ChoiceField(choices=choices, required=False)


class CharacterLootListForm(create_form("character_loot_list")):
    # providers can be world_npc or common_character
    npcs = CM.WORLD_NPCS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in npcs]

    characters = CM.CHARACTERS.all_with_base()
    choices.extend([(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in characters])

    provider = forms.ChoiceField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = forms.ChoiceField(choices=choices)

    # depends on quest
    choices = [("", "---------")]
    objects = CM.QUESTS.all_with_base()
    choices.extend([(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects])
    quest = forms.ChoiceField(choices=choices, required=False)


class QuestRewardListForm(create_form("quest_reward_list")):
    # providers must be object_creators
    objects = CM.QUESTS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    provider = forms.ChoiceField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = forms.ChoiceField(choices=choices)

    # depends on quest
    choices = [("", "---------")]
    objects = CM.QUESTS.all_with_base()
    choices.extend([(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects])
    quest = forms.ChoiceField(choices=choices, required=False)


class CommonObjectsForm(create_form("common_objects")):
    icon = ImageField(image_type="icon", required=False)


class PocketObjectsForm(create_form("pocket_objects")):
    pass


class FoodsForm(create_form("foods")):
    pass
        

class SkillBooksForm(create_form("skill_books")):
    # skills
    objects = CM.SKILLS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    skill = forms.ChoiceField(choices=choices)


class PropertiesDictForm(create_form("properties_dict")):
    pass


class CharactersForm(create_form("characters")):
    icon = ImageField(image_type="icon")

    choices = [("", "---------")]
    characters = CM.CHARACTERS.all_with_base()
    choices.extend([(obj["key"], obj["name"] + " (" + obj["element_type"] + " - " + obj["key"] + ")") for obj in characters])
    clone = forms.ChoiceField(choices=choices)


class PlayerCharactersForm(create_form("player_characters")):
    pass


class DefaultObjectsForm(create_form("default_objects")):
    # all character's
    objects = CM.CHARACTERS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    character = forms.ChoiceField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = forms.ChoiceField(choices=choices)


class ShopsForm(create_form("shops")):
    icon = ImageField(image_type="icon")


class ShopGoodsForm(create_form("shop_goods")):
    # all shops
    objects = CM.SHOPS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    shop = forms.ChoiceField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    goods = forms.ChoiceField(choices=choices)

    # available units are common objects
    objects = CM.COMMON_OBJECTS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    unit = forms.ChoiceField(choices=choices)


class NPCShopsForm(create_form("npc_shops")):
    # All NPCs.
    objects = CM.WORLD_NPCS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    npc = forms.ChoiceField(choices=choices)

    # All shops.
    objects = CM.SHOPS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    shop = forms.ChoiceField(choices=choices)


class SkillsForm(create_form("skills")):
    def __init__(self, *args, **kwargs):
        super(SkillsForm, self).__init__(*args, **kwargs)
        
        self.fields['icon'] = ImageField(image_type="icon", required=False)
        
        choices = [("", "---------")]
        objects = CM.SKILL_TYPES.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
        self.fields['main_type'] = forms.ChoiceField(choices=choices, required=False)
        self.fields['sub_type'] = forms.ChoiceField(choices=choices, required=False)


class SkillTypesForm(create_form("skill_types")):
    pass


class DefaultSkillsForm(create_form("default_skills")):
    # all character's models
    objects = CM.CHARACTERS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    character = forms.ChoiceField(choices=choices)

    objects = CM.SKILLS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    skill = forms.ChoiceField(choices=choices)


class NPCDialoguesForm(create_form("npc_dialogues")):
    # All NPCs.
    objects = CM.WORLD_NPCS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    npc = forms.ChoiceField(choices=choices)

    objects = CM.DIALOGUES.objects.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dialogue = forms.ChoiceField(choices=choices)


class QuestsForm(create_form("quests")):
    pass


class QuestObjectivesForm(create_form("quest_objectives")):
    objects = CM.QUESTS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    quest = forms.ChoiceField(choices=choices)

    choices = QUEST_OBJECTIVE_SET.choice_all()
    type = forms.ChoiceField(choices=choices)


class QuestDependenciesForm(create_form("quest_dependencies")):
    objects = CM.QUESTS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    quest = forms.ChoiceField(choices=choices)
    dependency = forms.ChoiceField(choices=choices)

    choices = QUEST_STATUS_SET.choice_all()
    type = forms.ChoiceField(choices=choices)


class DialogueQuestDependenciesForm(create_form("dialogue_quest_dependencies")):
    objects = CM.DIALOGUES.objects.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dialogue = forms.ChoiceField(choices=choices)

    objects = CM.QUESTS.all_with_base()
    choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
    dependency = forms.ChoiceField(choices=choices)

    choices = QUEST_STATUS_SET.choice_all()
    type = forms.ChoiceField(choices=choices)


class EquipmentsForm(create_form("equipments")):
    objects = CM.EQUIPMENT_POSITIONS.objects.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    position = forms.ChoiceField(choices=choices)

    objects = CM.EQUIPMENT_TYPES.objects.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    type = forms.ChoiceField(choices=choices)


class EventDataForm(create_form("event_data")):
    choices = EVENT_ACTION_SET.choice_all()
    action = forms.ChoiceField(choices=choices)

    choices = EVENT_TRIGGER_SET.choice_all()
    trigger_type = forms.ChoiceField(choices=choices)

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
        
        objects = CM.CHARACTERS.all_with_base()
        choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
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
        objects = CM.WORLD_NPCS.all_with_base()
        choices.extend([(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects])
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

        objects = CM.SKILLS.all_with_base()
        choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
        self.fields['skill'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.ACTION_LEARN_SKILL.model
        fields = '__all__'


class ActionAcceptQuestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ActionAcceptQuestForm, self).__init__(*args, **kwargs)

        objects = CM.EVENT_DATA.objects.filter(action="ACTION_ACCEPT_QUEST")
        choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
        self.fields['event_key'] = forms.ChoiceField(choices=choices)

        objects = CM.QUESTS.all_with_base()
        choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.ACTION_ACCEPT_QUEST.model
        fields = '__all__'
        
        
class ActionTurnInQuestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ActionTurnInQuestForm, self).__init__(*args, **kwargs)

        objects = CM.EVENT_DATA.objects.filter(action="ACTION_TURN_IN_QUEST")
        choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
        self.fields['event_key'] = forms.ChoiceField(choices=choices)

        objects = CM.QUESTS.all_with_base()
        choices = [(obj["key"], obj["name"] + " (" + obj["key"] + ")") for obj in objects]
        self.fields['quest'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.ACTION_TURN_IN_QUEST.model
        fields = '__all__'
        
        
class ActionCloseEventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ActionCloseEventForm, self).__init__(*args, **kwargs)

        objects = CM.EVENT_DATA.objects.filter(action="ACTION_CLOSE_EVENT")
        choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
        self.fields['event_key'] = forms.ChoiceField(choices=choices)

        objects = CM.EVENT_DATA.objects.all()
        choices = [(obj.key, obj.key) for obj in objects]
        self.fields['event'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = CM.ACTION_CLOSE_EVENT.model
        fields = '__all__'
        

class ActionMessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ActionMessageForm, self).__init__(*args, **kwargs)
        localize_form_fields(self)

    class Meta:
        model = EVENT_ACTION_SET.get("ACTION_MESSAGE").model()
        fields = '__all__'


class ActionGetObjectsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ActionGetObjectsForm, self).__init__(*args, **kwargs)

        # available objects
        choices = get_all_pocketable_objects()
        self.fields['object'] = forms.ChoiceField(choices=choices)

        localize_form_fields(self)

    class Meta:
        model = EVENT_ACTION_SET.get("ACTION_GET_OBJECTS").model()
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
"""
