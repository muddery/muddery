
from wtforms import validators, widgets
from wtforms.fields import SelectField
from muddery.server.mappings.quest_objective_set import QUEST_OBJECTIVE_SET
from muddery.server.mappings.quest_status_set import QUEST_STATUS_SET
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.server.mappings.event_trigger_set import EVENT_TRIGGER_SET
from muddery.server.database.worlddata_db import WorldDataDB
from muddery.worldeditor.dao import common_mappers as CM
from muddery.worldeditor.dao.general_querys import get_element_base_data
from muddery.worldeditor.forms.location_field import LocationField
from muddery.worldeditor.forms.image_field import ImageField
from muddery.worldeditor.forms.base_form import BaseForm
from muddery.worldeditor.utils.localized_strings import LocalizedStrings


def generate_choices(records, add_empty=False):
    """
    Generate a list of choices from a list of records.

    Args:
        records: records with key and name fields.
        add_empty: add an empty choice.
    """
    choices = [("", "---------")] if add_empty else []
    choices.extend([(r.key, (r.name + " (" + r.key + ")") if r.name else r.key) for r in records])
    return choices


def get_model(table_name):
    """
    Get a form of a table.
    """
    return WorldDataDB.inst().get_model(table_name)


def get_all_pocketable_objects():
    """
    Get all objects that can be put in player's pockets.
    """
    records = CM.COMMON_OBJECTS.all_with_base()
    return generate_choices(records)


class GameSettingsForm(BaseForm):
    records = get_element_base_data("ROOM")
    choices = generate_choices(records, add_empty=True)
    start_location_key = LocationField(choices=choices)
    default_player_home_key = LocationField(choices=choices)

    records = get_element_base_data("PLAYER_CHARACTER")
    choices = generate_choices(records, add_empty=True)
    default_player_character_key = SelectField(choices=choices)

    records = get_element_base_data("STAFF_CHARACTER")
    choices = generate_choices(records, add_empty=True)
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
    records = CM.WORLD_AREAS.all_with_base()
    choices = generate_choices(records, add_empty=True)
    area = SelectField(choices=choices)

    icon = ImageField(image_type="icon")

    background = ImageField(image_type="background")

    class Meta:
        model = get_model("world_rooms")


class WorldExitsForm(BaseForm):
    records = CM.WORLD_ROOMS.all_with_base()
    choices = generate_choices(records)
    location = LocationField(choices=choices)
    destination = LocationField(choices=choices)

    class Meta:
        model = get_model("world_exits")


class ExitLocks(BaseForm):
    class Meta:
        model = get_model("exit_locks")


class WorldObjectsForm(BaseForm):
    records = CM.WORLD_ROOMS.all_with_base()
    choices = generate_choices(records)
    location = LocationField(choices=choices)

    icon = ImageField(image_type="icon")

    class Meta:
        model = get_model("world_objects")


class WorldNPCsForm(BaseForm):
    # NPC's location
    records = CM.WORLD_ROOMS.all_with_base()
    choices = generate_choices(records)
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
    records = CM.OBJECT_CREATORS.all_with_base()
    choices = generate_choices(records)
    provider = SelectField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = SelectField(choices=choices)

    # depends on quest
    records = CM.QUESTS.all_with_base()
    choices = generate_choices(records, add_empty=True)
    quest = SelectField(choices=choices)

    class Meta:
        model = get_model("creator_loot_list")


class CharacterLootListForm(BaseForm):
    # providers can be world_npc or common_character
    npcs = CM.WORLD_NPCS.all_with_base()
    choices = generate_choices(npcs)

    characters = CM.CHARACTERS.all_with_base()
    choices.extend(generate_choices(characters))

    provider = SelectField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = SelectField(choices=choices)

    # depends on quest
    objects = CM.QUESTS.all_with_base()
    choices = generate_choices(objects, add_empty=True)
    quest = SelectField(choices=choices)

    class Meta:
        model = get_model("character_loot_list")


class QuestRewardListForm(BaseForm):
    # providers must be object_creators
    records = CM.QUESTS.all_with_base()
    choices = generate_choices(records)
    provider = SelectField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = SelectField(choices=choices)

    # depends on quest
    records = CM.QUESTS.all_with_base()
    choices = generate_choices(records, add_empty=True)
    quest = SelectField(choices=choices)

    class Meta:
        model = get_model("quest_reward_list")


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
    records = CM.SKILLS.all_with_base()
    choices = generate_choices(records)
    skill = SelectField(choices=choices)

    class Meta:
        model = get_model("skill_books")


class PropertiesDictForm(BaseForm):
    class Meta:
        model = get_model("properties_dict")


class CharactersForm(BaseForm):
    icon = ImageField(image_type="icon")

    choices = [("", "---------")]
    records = CM.CHARACTERS.all_with_base()
    choices.extend([(r.key, (r.name + " (" + r.element_type + " - " + r.key + ")") if r.name else
                    r.element_type + " - " + r.key) for r in records])
    clone = SelectField(choices=choices)

    class Meta:
        model = get_model("characters")


class PlayerCharactersForm(BaseForm):
    class Meta:
        model = get_model("player_characters")


class DefaultObjectsForm(BaseForm):
    # all character's
    records = CM.CHARACTERS.all_with_base()
    choices = generate_choices(records)
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
    records = CM.SHOPS.all_with_base()
    choices = generate_choices(records)
    shop = SelectField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    goods = SelectField(choices=choices)

    # available units are common objects
    records = CM.COMMON_OBJECTS.all_with_base()
    choices = generate_choices(records)
    unit = SelectField(choices=choices)

    class Meta:
        model = get_model("shop_goods")


class NPCShopsForm(BaseForm):
    # All NPCs.
    records = CM.WORLD_NPCS.all_with_base()
    choices = generate_choices(records)
    npc = SelectField(choices=choices)

    # All shops.
    records = CM.SHOPS.all_with_base()
    choices = generate_choices(records)
    shop = SelectField(choices=choices)

    class Meta:
        model = get_model("npc_shops")


class SkillsForm(BaseForm):
    icon = ImageField(image_type="icon")

    records = CM.SKILL_TYPES.all()
    choices = generate_choices(records, add_empty=True)
    main_type = SelectField(choices=choices)
    sub_type = SelectField(choices=choices)

    class Meta:
        model = get_model("skills")


class SkillTypesForm(BaseForm):
    class Meta:
        model = get_model("skill_types")


class DefaultSkillsForm(BaseForm):
    # all character's models
    records = CM.CHARACTERS.all_with_base()
    choices = generate_choices(records)
    character = SelectField(choices=choices)

    records = CM.SKILLS.all_with_base()
    choices = generate_choices(records)
    skill = SelectField(choices=choices)

    class Meta:
        model = get_model("default_skills")


class NPCDialoguesForm(BaseForm):
    # All NPCs.
    records = CM.WORLD_NPCS.all_with_base()
    choices = generate_choices(records)
    npc = SelectField(choices=choices)

    records = CM.DIALOGUES.all()
    choices = generate_choices(records)
    dialogue = SelectField(choices=choices)

    class Meta:
        model = get_model("npc_dialogues")


class QuestsForm(BaseForm):
    class Meta:
        model = get_model("quests")


class QuestObjectivesForm(BaseForm):
    records = CM.QUESTS.all_with_base()
    choices = generate_choices(records)
    quest = SelectField(choices=choices)

    objectives = QUEST_OBJECTIVE_SET.all()
    choices = [(key, "%s (%s)" % (LocalizedStrings.inst().trans(key, category = "quest_objective"), key))
               for key in objectives]
    type = SelectField(choices=choices)

    class Meta:
        model = get_model("quest_objectives")


class QuestDependenciesForm(BaseForm):
    records = CM.QUESTS.all_with_base()
    choices = generate_choices(records)
    quest = SelectField(choices=choices)
    dependency = SelectField(choices=choices)

    choices = QUEST_STATUS_SET.choice_all()
    type = SelectField(choices=choices)

    class Meta:
        model = get_model("quest_dependencies")


class DialogueQuestDependenciesForm(BaseForm):
    records = CM.DIALOGUES.all()
    choices = generate_choices(records)
    dialogue = SelectField(choices=choices)

    records = CM.QUESTS.all_with_base()
    choices = generate_choices(records)
    dependency = SelectField(choices=choices)

    choices = QUEST_STATUS_SET.choice_all()
    type = SelectField(choices=choices)

    class Meta:
        model = get_model("dialogue_quest_dependencies")


class EquipmentsForm(BaseForm):
    records = CM.EQUIPMENT_POSITIONS.all()
    choices = generate_choices(records)
    position = SelectField(choices=choices)

    records = CM.EQUIPMENT_TYPES.all()
    choices = generate_choices(records)
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
    records = CM.EVENT_DATA.filter({"action": "ACTION_ATTACK"})
    choices = [(r.key, r.key) for r in records]
    event_key = SelectField(choices=choices)

    records = CM.CHARACTERS.all_with_base()
    choices = generate_choices(records)
    mob = SelectField(choices=choices)

    class Meta:
        model = get_model("action_attack")


class ActionDialogueForm(BaseForm):
    records = CM.EVENT_DATA.filter({"action": "ACTION_DIALOGUE"})
    choices = [(r.key, r.key) for r in records]
    event_key = SelectField(choices=choices)

    records = CM.DIALOGUES.all()
    choices = generate_choices(records)
    dialogue = SelectField(choices=choices)

    # NPCs
    records = CM.WORLD_NPCS.all_with_base()
    choices = generate_choices(records, add_empty=True)
    npc = SelectField(choices=choices)

    class Meta:
        model = get_model("action_dialogue")


class ActionLearnSkillForm(BaseForm):
    records = CM.EVENT_DATA.filter({"action": "ACTION_LEARN_SKILL"})
    choices = [(r.key, r.key) for r in records]
    event_key = SelectField(choices=choices)

    records = CM.SKILLS.all_with_base()
    choices = generate_choices(records)
    skill = SelectField(choices=choices)

    class Meta:
        model = get_model("action_learn_skill")


class ActionAcceptQuestForm(BaseForm):
    records = CM.EVENT_DATA.filter({"action": "ACTION_ACCEPT_QUEST"})
    choices = [(r.key, r.key) for r in records]
    event_key = SelectField(choices=choices)

    records = CM.QUESTS.all_with_base()
    choices = generate_choices(records)
    quest = SelectField(choices=choices)

    class Meta:
        model = get_model("action_accept_quest")

        
class ActionTurnInQuestForm(BaseForm):
    records = CM.EVENT_DATA.filter({"action": "ACTION_TURN_IN_QUEST"})
    choices = [(r.key, r.key) for r in records]
    event_key = SelectField(choices=choices)

    records = CM.QUESTS.all_with_base()
    choices = generate_choices(records)
    quest = SelectField(choices=choices)

    class Meta:
        model = get_model("action_turn_in_quest")

        
class ActionCloseEventForm(BaseForm):
    records = CM.EVENT_DATA.filter({"action": "ACTION_CLOSE_EVENT"})
    choices = [(r.key, r.key) for r in records]
    event_key = SelectField(choices=choices)

    records = CM.EVENT_DATA.all()
    choices = [(r.key, r.key) for r in records]
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
    records = CM.DIALOGUES.all()
    choices = generate_choices(records)
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
