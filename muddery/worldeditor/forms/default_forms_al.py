
from wtforms import Form, validators, widgets
from wtforms.fields import SelectField
from muddery.server.utils.localiztion_handler import localize_form_fields
from muddery.server.mappings.quest_objective_set import QUEST_OBJECTIVE_SET
from muddery.server.mappings.quest_status_set import QUEST_STATUS_SET
from muddery.server.mappings.event_action_set import EVENT_ACTION_SET
from muddery.server.mappings.event_trigger_set import EVENT_TRIGGER_SET
from muddery.worldeditor.dao import common_mappers as CM
from muddery.worldeditor.dao.general_querys import get_element_base_data
from muddery.worldeditor.forms.location_field import LocationField
from muddery.worldeditor.forms.image_field import ImageField
from muddery.worldeditor.forms.create_form import create_form


def get_all_pocketable_objects():
    """
    Get all objects that can be put in player's pockets.
    """
    records = CM.COMMON_OBJECTS.all_with_base()
    return [(r.key, r.name + " (" + r.key + ")") for r in records]


class GameSettingsForm(create_form("game_settings")):
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
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
    area = SelectField(choices=choices)

    icon = ImageField(image_type="icon")

    background = ImageField(image_type="background")


class WorldExitsForm(create_form("world_exits")):
    rooms = CM.WORLD_ROOMS.all_with_base()
    choices = [(r.key, r.name + " (" + r.key + ")") for r in rooms]
    location = LocationField(choices=choices)
    destination = LocationField(choices=choices)


class WorldObjectsForm(create_form("world_objects")):
    rooms = CM.WORLD_ROOMS.all_with_base()
    choices = [(r.key, r.name + " (" + r.key + ")") for r in rooms]
    location = LocationField(choices=choices)

    icon = ImageField(image_type="icon")


class WorldNPCsForm(create_form("world_npcs")):
    # NPC's location
    rooms = CM.WORLD_ROOMS.all_with_base()
    choices = [(r.key, r.name + " (" + r.key + ")") for r in rooms]
    location = LocationField(choices=choices)


class ObjectCreatorsForm(create_form("object_creators")):
    pass


class CreatorLootListForm(create_form("creator_loot_list")):
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


class CharacterLootListForm(create_form("character_loot_list")):
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


class QuestRewardListForm(create_form("quest_reward_list")):
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


class CommonObjectsForm(create_form("common_objects")):
    icon = ImageField(image_type="icon")


class PocketObjectsForm(create_form("pocket_objects")):
    pass


class FoodsForm(create_form("foods")):
    pass
        

class SkillBooksForm(create_form("skill_books")):
    # skills
    objects = CM.SKILLS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    skill = SelectField(choices=choices)


class PropertiesDictForm(create_form("properties_dict")):
    pass


class CharactersForm(create_form("characters")):
    icon = ImageField(image_type="icon")

    choices = [("", "---------")]
    characters = CM.CHARACTERS.all_with_base()
    choices.extend([(obj.key, obj.name + " (" + obj.element_type + " - " + obj.key + ")") for obj in characters])
    clone = SelectField(choices=choices)


class PlayerCharactersForm(create_form("player_characters")):
    pass


class DefaultObjectsForm(create_form("default_objects")):
    # all character's
    objects = CM.CHARACTERS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    character = SelectField(choices=choices)

    # available objects
    choices = get_all_pocketable_objects()
    object = SelectField(choices=choices)


class ShopsForm(create_form("shops")):
    icon = ImageField(image_type="icon")


class ShopGoodsForm(create_form("shop_goods")):
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


class NPCShopsForm(create_form("npc_shops")):
    # All NPCs.
    objects = CM.WORLD_NPCS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    npc = SelectField(choices=choices)

    # All shops.
    objects = CM.SHOPS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    shop = SelectField(choices=choices)


class SkillsForm(create_form("skills")):
    icon = ImageField(image_type="icon")

    choices = [("", "---------")]
    objects = CM.SKILL_TYPES.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])
    main_type = SelectField(choices=choices)
    sub_type = SelectField(choices=choices)


class SkillTypesForm(create_form("skill_types")):
    pass


class DefaultSkillsForm(create_form("default_skills")):
    # all character's models
    objects = CM.CHARACTERS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    character = SelectField(choices=choices)

    objects = CM.SKILLS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    skill = SelectField(choices=choices)


class NPCDialoguesForm(create_form("npc_dialogues")):
    # All NPCs.
    objects = CM.WORLD_NPCS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    npc = SelectField(choices=choices)

    objects = CM.DIALOGUES.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dialogue = SelectField(choices=choices)


class QuestsForm(create_form("quests")):
    pass


class QuestObjectivesForm(create_form("quest_objectives")):
    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    quest = SelectField(choices=choices)

    choices = QUEST_OBJECTIVE_SET.choice_all()
    type = SelectField(choices=choices)


class QuestDependenciesForm(create_form("quest_dependencies")):
    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    quest = SelectField(choices=choices)
    dependency = SelectField(choices=choices)

    choices = QUEST_STATUS_SET.choice_all()
    type = SelectField(choices=choices)


class DialogueQuestDependenciesForm(create_form("dialogue_quest_dependencies")):
    objects = CM.DIALOGUES.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dialogue = SelectField(choices=choices)

    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dependency = SelectField(choices=choices)

    choices = QUEST_STATUS_SET.choice_all()
    type = SelectField(choices=choices)


class EquipmentsForm(create_form("equipments")):
    objects = CM.EQUIPMENT_POSITIONS.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    position = SelectField(choices=choices)

    objects = CM.EQUIPMENT_TYPES.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    type = SelectField(choices=choices)


class EventDataForm(create_form("event_data")):
    choices = EVENT_ACTION_SET.choice_all()
    action = SelectField(choices=choices)

    choices = EVENT_TRIGGER_SET.choice_all()
    trigger_type = SelectField(choices=choices)


class ActionAttackForm(create_form("action_attack")):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_ATTACK"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.CHARACTERS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    mob = SelectField(choices=choices)


class ActionDialogueForm(create_form("action_dialogue")):
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


class ActionLearnSkillForm(create_form("action_learn_skill")):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_LEARN_SKILL"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.SKILLS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    skill = SelectField(choices=choices)


class ActionAcceptQuestForm(create_form("action_accept_quest")):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_ACCEPT_QUEST"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    quest = SelectField(choices=choices)

        
class ActionTurnInQuestForm(create_form("action_turn_in_quest")):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_TURN_IN_QUEST"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.QUESTS.all_with_base()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    quest = SelectField(choices=choices)

        
class ActionCloseEventForm(create_form("action_close_event")):
    objects = CM.EVENT_DATA.filter({"action": "ACTION_CLOSE_EVENT"})
    choices = [(obj.key, obj.key + " (" + obj.key + ")") for obj in objects]
    event_key = SelectField(choices=choices)

    objects = CM.EVENT_DATA.all()
    choices = [(obj.key, obj.key) for obj in objects]
    event = SelectField(choices=choices)


class ActionMessageForm(create_form("action_message")):
    pass


class ActionGetObjectsForm(create_form("action_get_objects")):
    # available objects
    choices = get_all_pocketable_objects()
    object = SelectField(choices=choices)


class DialoguesForm(create_form("dialogues")):
    pass


class DialogueRelationsForm(create_form("dialogue_relations")):
    objects = CM.DIALOGUES.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]
    dialogue = SelectField(choices=choices)
    next_dlg = SelectField(choices=choices)


class LocalizedStringsForm(create_form("localized_strings")):
    pass


class ImageResourcesForm(create_form("image_resources")):
    choices = [
        ("background", "background"),
        ("icon", "icon"),
    ]
    type = SelectField(choices=choices)
