
from wtforms import validators, widgets
from wtforms.fields import SelectField
from muddery.server.mappings.quest_objective_set import QUEST_OBJECTIVE_SET
from muddery.server.mappings.quest_status_set import QUEST_STATUS_SET
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.server.mappings.event_trigger_set import EVENT_TRIGGER_SET
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.database.db_manager import DBManager
from muddery.worldeditor.dao import common_mappers as CM
from muddery.worldeditor.dao.general_querys import get_element_base_data
from muddery.worldeditor.forms.location_field import LocationField
from muddery.worldeditor.forms.image_field import ImageField
from muddery.worldeditor.forms.base_form import BaseForm


def get_model(table_name):
    """
    Get a form of a table.
    """
    session_name = SETTINGS.WORLD_DATA_APP
    return DBManager.inst().get_model(session_name, table_name)


def get_all_pocketable_objects():
    """
    Get all objects that can be put in player's pockets.
    """
    records = CM.COMMON_OBJECTS.all_with_base()
    return [(r.key, r.name + " (" + r.key + ")") for r in records]


class GameSettingsForm(BaseForm):
    choices = [("", "---------")]
    records = get_element_base_data("ROOM")
    choices.extend([(record.key, record.name + " (" + record.key + ")") for record in records])
    start_location_key = LocationField(choices=choices)
    default_player_home_key = LocationField(choices=choices)

    choices = [("", "---------")]
    records = get_element_base_data("PLAYER_CHARACTER")
    choices.extend([(record.key, record.name + " (" + record.key + ")") for record in records])
    default_player_character_key = SelectField(choices=choices)

    choices = [("", "---------")]
    records = get_element_base_data("STAFF_CHARACTER")
    choices.extend([(record.key, record.name + " (" + record.key + ")") for record in records])
    default_staff_character_key = SelectField(choices=choices)

    class Meta:
        model = get_model("game_settings")


class HonourSettingsForm(BaseForm):
    class Meta:
        model = get_model("honour_settings")


class EquipmentTypesForm(BaseForm):
    class Meta:
        model = get_model("equipment_types")


class EquipmentPositionsForm(BaseForm):
    class Meta:
        model = get_model("equipment_positions")


class WorldAreasForm(BaseForm):
    background = ImageField(image_type="background")

    class Meta:
        model = get_model("world_areas")


class WorldRoomsForm(BaseForm):
    choices = [("", "---------")]
    objects = CM.WORLD_AREAS.all_with_base()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
    area = SelectField(choices=choices)

    icon = ImageField(image_type="icon")

    background = ImageField(image_type="background")

    class Meta:
        model = get_model("world_rooms")


class WorldExitsForm(BaseForm):
    rooms = CM.WORLD_ROOMS.all_with_base()
    choices = [(r.key, r.name + " (" + r.key + ")") for r in rooms]
    location = LocationField(choices=choices)
    destination = LocationField(choices=choices)

    class Meta:
        model = get_model("world_exits")


class ExitLocks(BaseForm):
    class Meta:
        model = get_model("exit_locks")


class WorldObjectsForm(BaseForm):
    rooms = CM.WORLD_ROOMS.all_with_base()
    choices = [(r.key, r.name + " (" + r.key + ")") for r in rooms]
    location = LocationField(choices=choices)

    icon = ImageField(image_type="icon")

    class Meta:
        model = get_model("world_objects")


class WorldNPCsForm(BaseForm):
    # NPC's location
    rooms = CM.WORLD_ROOMS.all_with_base()
    choices = [(r.key, r.name + " (" + r.key + ")") for r in rooms]
    location = LocationField(choices=choices)

    class Meta:
        model = get_model("world_npcs")


class ConditionalDesc(BaseForm):
    class Meta:
        model = get_model("conditional_desc")


class ObjectCreatorsForm(BaseForm):
    class Meta:
        model = get_model("object_creators")


class CreatorLootListForm(BaseForm):
    # providers must be object_creators
    objects = CM.OBJECT_CREATORS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    provider = SelectField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = SelectField(choices=choices)

    # depends on quest
    choices = [("", "---------")]
    objects = CM.QUESTS.all_with_base()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
    quest = SelectField(choices=choices)

    class Meta:
        model = get_model("creator_loot_list")


class CharacterLootListForm(BaseForm):
    # providers can be world_npc or common_character
    npcs = CM.WORLD_NPCS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in npcs]

    characters = CM.CHARACTERS.all_with_base()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in characters])

    provider = SelectField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = SelectField(choices=choices)

    # depends on quest
    choices = [("", "---------")]
    objects = CM.QUESTS.all_with_base()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
    quest = SelectField(choices=choices)

    class Meta:
        model = get_model("character_loot_list")


class QuestRewardListForm(BaseForm):
    # providers must be object_creators
    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    provider = SelectField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = SelectField(choices=choices)

    # depends on quest
    choices = [("", "---------")]
    objects = CM.QUESTS.all_with_base()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
    quest = SelectField(choices=choices)

    class Meta:
        model = get_model("character_loot_list")


class CommonObjectsForm(BaseForm):
    icon = ImageField(image_type="icon")

    class Meta:
        model = get_model("common_objects")


class PocketObjectsForm(BaseForm):
    class Meta:
        model = get_model("pocket_objects")


class FoodsForm(BaseForm):
    class Meta:
        model = get_model("foods")
        

class SkillBooksForm(BaseForm):
    # skills
    objects = CM.SKILLS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    skill = SelectField(choices=choices)

    class Meta:
        model = get_model("skill_books")


class PropertiesDictForm(BaseForm):
    class Meta:
        model = get_model("properties_dict")


class CharactersForm(BaseForm):
    icon = ImageField(image_type="icon")

    choices = [("", "---------")]
    characters = CM.CHARACTERS.all_with_base()
    choices.extend([(obj.key, obj.name + " (" + obj.element_type + " - " + obj.key + ")") for obj in characters])
    clone = SelectField(choices=choices)

    class Meta:
        model = get_model("characters")


class PlayerCharactersForm(BaseForm):
    class Meta:
        model = get_model("player_characters")


class DefaultObjectsForm(BaseForm):
    # all character's
    objects = CM.CHARACTERS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    character = SelectField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = SelectField(choices=choices)

    class Meta:
        model = get_model("default_objects")


class ShopsForm(BaseForm):
    icon = ImageField(image_type="icon")

    class Meta:
        model = get_model("shops")


class ShopGoodsForm(BaseForm):
    # all shops
    objects = CM.SHOPS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    shop = SelectField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    goods = SelectField(choices=choices)

    # available units are common objects
    objects = CM.COMMON_OBJECTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    unit = SelectField(choices=choices)

    class Meta:
        model = get_model("shop_goods")


class NPCShopsForm(BaseForm):
    # All NPCs.
    objects = CM.WORLD_NPCS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    npc = SelectField(choices=choices)

    # All shops.
    objects = CM.SHOPS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    shop = SelectField(choices=choices)

    class Meta:
        model = get_model("npc_shops")


class SkillsForm(BaseForm):
    icon = ImageField(image_type="icon")

    choices = [("", "---------")]
    objects = CM.SKILL_TYPES.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
    main_type = SelectField(choices=choices)
    sub_type = SelectField(choices=choices)

    class Meta:
        model = get_model("skills")


class SkillTypesForm(BaseForm):
    class Meta:
        model = get_model("skill_types")


class DefaultSkillsForm(BaseForm):
    # all character's models
    objects = CM.CHARACTERS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    character = SelectField(choices=choices)

    objects = CM.SKILLS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    skill = SelectField(choices=choices)

    class Meta:
        model = get_model("default_skills")


class NPCDialoguesForm(BaseForm):
    # All NPCs.
    objects = CM.WORLD_NPCS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    npc = SelectField(choices=choices)

    objects = CM.DIALOGUES.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dialogue = SelectField(choices=choices)

    class Meta:
        model = get_model("npc_dialogues")


class QuestsForm(BaseForm):
    class Meta:
        model = get_model("quests")


class QuestObjectivesForm(BaseForm):
    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    quest = SelectField(choices=choices)

    choices = QUEST_OBJECTIVE_SET.choice_all()
    type = SelectField(choices=choices)

    class Meta:
        model = get_model("quest_objectives")


class QuestDependenciesForm(BaseForm):
    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    quest = SelectField(choices=choices)
    dependency = SelectField(choices=choices)

    choices = QUEST_STATUS_SET.choice_all()
    type = SelectField(choices=choices)

    class Meta:
        model = get_model("quest_dependencies")


class DialogueQuestDependenciesForm(BaseForm):
    objects = CM.DIALOGUES.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dialogue = SelectField(choices=choices)

    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dependency = SelectField(choices=choices)

    choices = QUEST_STATUS_SET.choice_all()
    type = SelectField(choices=choices)

    class Meta:
        model = get_model("dialogue_quest_dependencies")


class EquipmentsForm(BaseForm):
    objects = CM.EQUIPMENT_POSITIONS.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    position = SelectField(choices=choices)

    objects = CM.EQUIPMENT_TYPES.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    type = SelectField(choices=choices)

    class Meta:
        model = get_model("equipments")


class EventDataForm(BaseForm):
    choices = EVENT_ACTION_SET.choice_all()
    action = SelectField(choices=choices)

    choices = EVENT_TRIGGER_SET.choice_all()
    trigger_type = SelectField(choices=choices)

    class Meta:
        model = get_model("event_data")


class ActionAttackForm(BaseForm):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_ATTACK"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.CHARACTERS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    mob = SelectField(choices=choices)

    class Meta:
        model = get_model("action_attack")


class ActionDialogueForm(BaseForm):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_DIALOGUE"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.DIALOGUES.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dialogue = SelectField(choices=choices)

    # NPCs
    choices = [("", "---------")]
    objects = CM.WORLD_NPCS.all_with_base()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
    npc = SelectField(choices=choices)

    class Meta:
        model = get_model("action_dialogue")


class ActionLearnSkillForm(BaseForm):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_LEARN_SKILL"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.SKILLS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    skill = SelectField(choices=choices)

    class Meta:
        model = get_model("action_learn_skill")


class ActionAcceptQuestForm(BaseForm):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_ACCEPT_QUEST"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    quest = SelectField(choices=choices)

    class Meta:
        model = get_model("action_accept_quest")

        
class ActionTurnInQuestForm(BaseForm):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_TURN_IN_QUEST"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    quest = SelectField(choices=choices)

    class Meta:
        model = get_model("action_turn_in_quest")

        
class ActionCloseEventForm(BaseForm):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_CLOSE_EVENT"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.EVENT_DATA.all()
    choices = [(obj.key, obj.key) for obj in objects]
    event = SelectField(choices=choices)

    class Meta:
        model = get_model("action_close_event")


class ActionMessageForm(BaseForm):
    class Meta:
        model = get_model("action_message")


class ActionGetObjectsForm(BaseForm):
    # available objects
    choices = get_all_pocketable_objects()
    object = SelectField(choices=choices)

    class Meta:
        model = get_model("action_get_objects")


class DialoguesForm(BaseForm):
    class Meta:
        model = get_model("dialogues")


class DialogueRelationsForm(BaseForm):
    objects = CM.DIALOGUES.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dialogue = SelectField(choices=choices)
    next_dlg = SelectField(choices=choices)

    class Meta:
        model = get_model("dialogue_relations")


class LocalizedStringsForm(BaseForm):
    class Meta:
        model = get_model("localized_strings")


class ImageResourcesForm(BaseForm):
    choices = [
        ("background", "background"),
        ("icon", "icon"),
    ]
    type = SelectField(choices=choices)

    class Meta:
        model = get_model("image_resources")
