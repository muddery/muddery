from django.contrib import admin

import forms
from models import *
from muddery.worlddata import admin_base


# Register your models here.

class GameSettingsAdmin(admin_base.GameSettingsAdmin):
    form = forms.GameSettingsForm


class ClientSettingsAdmin(admin_base.ClientSettingsAdmin):
    pass


class ClassCategoriesAdmin(admin_base.ClassCategoriesAdmin):
    pass


class TypeclassesAdmin(admin_base.TypeclassesAdmin):
    pass


class WorldRoomsAdmin(admin_base.WorldRoomsAdmin):
    form = forms.WorldRoomsForm


class WorldExitsAdmin(admin_base.WorldExitsAdmin):
    form = forms.WorldExitsForm


class ExitLocksAdmin(admin_base.ExitLocksAdmin):
    form = forms.ExitLocksForm


class WorldObjectsAdmin(admin_base.WorldObjectsAdmin):
    form = forms.WorldObjectsForm


class ObjectCreatorsAdmin(admin_base.ObjectCreatorsAdmin):
    form = forms.ObjectCreatorsForm


class CreatorLootListAdmin(admin_base.CreatorLootListAdmin):
    form = forms.CreatorLootListForm


class CommonObjectsAdmin(admin_base.CommonObjectsAdmin):
    form = forms.CommonObjectsForm


class FoodsAdmin(admin_base.FoodsAdmin):
    pass


class EquipmentTypesAdmin(admin_base.EquipmentTypesAdmin):
    pass


class EquipmentPositionsAdmin(admin_base.EquipmentPositionsAdmin):
    pass


class EquipmentsAdmin(admin_base.EquipmentsAdmin):
    pass


class CharacterCareersAdmin(admin_base.CharacterCareersAdmin):
    pass


class CareersEquipmentsAdmin(admin_base.CareersEquipmentsAdmin):
    pass


class CharacterModelsAdmin(admin_base.CharacterModelsAdmin):
    pass


class WorldNPCAdmin(admin_base.WorldNPCAdmin):
    form = forms.CharacterForm


class CommonCharactersAdmin(admin_base.CommonCharactersAdmin):
    form = forms.CharacterForm


class CharacterLootListAdmin(admin_base.CharacterLootListAdmin):
    form = forms.CharacterLootListForm


class SkillsAdmin(admin_base.SkillsAdmin):
    form = forms.SkillsForm


class DefaultSkillsAdmin(admin_base.DefaultSkillsAdmin):
    form = forms.DefaultSkillsForm


class QuestsAdmin(admin_base.QuestsAdmin):
    form = forms.QuestsForm


class QuestRewardListAdmin(admin_base.QuestRewardListAdmin):
    form = forms.QuestRewardListForm


class QuestObjectiveTypesAdmin(admin_base.QuestObjectiveTypesAdmin):
    pass


class QuestObjectivesAdmin(admin_base.QuestObjectivesAdmin):
    pass


class QuestDependencyTypesAdmin(admin_base.QuestDependencyTypesAdmin):
    pass


class QuestDependenciesAdmin(admin_base.QuestDependenciesAdmin):
    pass


class EventTypesAdmin(admin_base.EventTypesAdmin):
    pass


class EventTriggerTypesAdmin(admin_base.EventTriggerTypesAdmin):
    pass


class EventDataAdmin(admin_base.EventDataAdmin):
    pass


class DialoguesAdmin(admin_base.DialoguesAdmin):
    pass


class DialogueQuestDependenciesAdmin(admin_base.DialogueQuestDependenciesAdmin):
    pass


class DialogueRelationsAdmin(admin_base.DialogueRelationsAdmin):
    pass


class DialogueSentencesAdmin(admin_base.DialogueSentencesAdmin):
    pass


class NPCDialoguesAdmin(admin_base.NPCDialoguesAdmin):
    pass


class EventAttacksAdmin(admin_base.EventAttacksAdmin):
    pass


class EventDialoguesAdmin(admin_base.EventDialoguesAdmin):
    pass


class LocalizedStringsAdmin(admin_base.LocalizedStringsAdmin):
    pass


admin.site.register(game_settings, GameSettingsAdmin)
admin.site.register(client_settings, ClientSettingsAdmin)
admin.site.register(class_categories, ClassCategoriesAdmin)
admin.site.register(typeclasses, TypeclassesAdmin)
admin.site.register(world_rooms, WorldRoomsAdmin)
admin.site.register(world_exits, WorldExitsAdmin)
admin.site.register(exit_locks, ExitLocksAdmin)
admin.site.register(world_objects, WorldObjectsAdmin)
admin.site.register(object_creators, ObjectCreatorsAdmin)
admin.site.register(creator_loot_list, CreatorLootListAdmin)
admin.site.register(common_objects, CommonObjectsAdmin)
admin.site.register(foods, FoodsAdmin)
admin.site.register(equipment_types, EquipmentTypesAdmin)
admin.site.register(equipment_positions, EquipmentPositionsAdmin)
admin.site.register(equipments, EquipmentsAdmin)
admin.site.register(character_careers, CharacterCareersAdmin)
admin.site.register(career_equipments, CareersEquipmentsAdmin)
admin.site.register(character_models, CharacterModelsAdmin)
admin.site.register(world_npcs, WorldNPCAdmin)
admin.site.register(common_characters, CommonCharactersAdmin)
admin.site.register(character_loot_list, CharacterLootListAdmin)
admin.site.register(skills, SkillsAdmin)
admin.site.register(default_skills, DefaultSkillsAdmin)
admin.site.register(quests, QuestsAdmin)
admin.site.register(quest_reward_list, QuestRewardListAdmin)
admin.site.register(quest_objective_types, QuestObjectiveTypesAdmin)
admin.site.register(quest_objectives, QuestObjectivesAdmin)
admin.site.register(quest_dependency_types, QuestDependencyTypesAdmin)
admin.site.register(quest_dependencies, QuestDependenciesAdmin)
admin.site.register(event_types, EventTypesAdmin)
admin.site.register(event_trigger_types, EventTriggerTypesAdmin)
admin.site.register(event_data, EventDataAdmin)
admin.site.register(dialogues, DialoguesAdmin)
admin.site.register(dialogue_quest_dependencies, DialogueQuestDependenciesAdmin)
admin.site.register(dialogue_relations, DialogueRelationsAdmin)
admin.site.register(dialogue_sentences, DialogueSentencesAdmin)
admin.site.register(npc_dialogues, NPCDialoguesAdmin)
admin.site.register(event_attacks, EventAttacksAdmin)
admin.site.register(event_dialogues, EventDialoguesAdmin)
admin.site.register(localized_strings, LocalizedStringsAdmin)

