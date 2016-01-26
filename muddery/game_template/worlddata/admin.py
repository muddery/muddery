from django.contrib import admin

from form import *
from models import *
from muddery.worlddata import admin_base


# Register your models here.


class ClassCategoriesAdmin(admin_base.ClassCategoriesAdmin):
    pass


class TypeclassesAdmin(admin_base.TypeclassesAdmin):
    pass


class WorldRoomsAdmin(admin_base.WorldRoomsAdmin):
    form = WorldRoomsForm


class WorldExitsAdmin(admin_base.WorldExitsAdmin):
    form = WorldExitsForm


class ExitLocksAdmin(admin_base.ExitLocksAdmin):
    form = ExitLocksForm


class WorldObjectsAdmin(admin_base.WorldObjectsAdmin):
    form = WorldObjectsForm


class ObjectCreatorsAdmin(admin_base.ObjectCreatorsAdmin):
    form = ObjectCreatorsForm


class LootListAdmin(admin_base.LootListAdmin):
    form = LootListForm


class CommonObjectsAdmin(admin_base.CommonObjectsAdmin):
    form = CommonObjectsForm


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
    form = CharacterForm


class CommonCharactersAdmin(admin_base.CommonCharactersAdmin):
    form = CharacterForm


class SkillsAdmin(admin_base.SkillsAdmin):
    form = SkillsForm


class DefaultSkillsAdmin(admin_base.DefaultSkillsAdmin):
    form = DefaultSkillsForm


class QuestsAdmin(admin_base.QuestsAdmin):
    form = QuestsForm


class QuestObjectiveTypesAdmin(admin_base.QuestObjectiveTypesAdmin):
    pass


class QuestObjectivesAdmin(admin_base.QuestObjectivesAdmin):
    pass


class QuestDependencyTypesAdmin(admin_base.QuestDependencyTypesAdmin):
    pass


class QuestDependenciesAdmin(admin_base.QuestDependenciesAdmin):
    pass


class EventDataAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'object',
                    'type',
                    'trigger',
                    'condition')


class DialoguesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'condition',
                    'get_have_quest')
    def get_have_quest(self, obj):
        if obj.have_quest:
            return obj.have_quest.key
    form = DialoguesForm


class DialogueRelationsAdmin(admin.ModelAdmin):
    list_display = ('get_dialogue',
                    'get_next')
    def get_dialogue(self, obj):
        return obj.dialogue.key
    def get_next(self, obj):
        return obj.next.key
    form = DialogueRelationsForm


class DialogueSentencesAdmin(admin.ModelAdmin):
    list_display = ('get_dialogue',
                    'ordinal',
                    'speaker',
                    'content',
                    'action',
                    'get_provide_quest',
                    'get_complete_quest')
    def get_dialogue(self, obj):
        return obj.dialogue.key
    def get_provide_quest(self, obj):
        if obj.provide_quest:
            return obj.provide_quest.key
    def get_complete_quest(self, obj):
        if obj.complete_quest:
            return obj.complete_quest.key
    form = DialogueSentencesForm


class NPCDialoguesAdmin(admin.ModelAdmin):
    list_display = ('get_npc',
                    'get_dialogue',
                    'default')
    def get_npc(self, obj):
        return obj.npc.key
    def get_dialogue(self, obj):
        return obj.dialogue.key
    form = NPCDialoguesForm


class DialogueQuestDependencyAdmin(admin.ModelAdmin):
    list_display = ('get_dialogue',
                    'get_dependency',
                    'type')
    def get_dialogue(self, obj):
        return obj.dialogue.key
    def get_dependency(self, obj):
        return obj.dependency.key
    form = DialogueQuestDependencyForm


class CharacterModelsAdmin(admin.ModelAdmin):
    list_display = ('character',
                    'level',
                    'max_exp',
                    'max_hp',
                    'max_mp',
                    'attack',
                    'defence')


class EventMobsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'mob',
                    'level',
                    'odds',
                    'desc')


class EventDialoguesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'dialogue',
                    'npc')
    form = EventDialoguesForm


class LocalizedStringsAdmin(admin.ModelAdmin):
    list_display = ('origin',
                    'local')


admin.site.register(class_categories, ClassCategoriesAdmin)
admin.site.register(typeclasses, TypeclassesAdmin)
admin.site.register(world_rooms, WorldRoomsAdmin)
admin.site.register(world_exits, WorldExitsAdmin)
admin.site.register(exit_locks, ExitLocksAdmin)
admin.site.register(world_objects, WorldObjectsAdmin)
admin.site.register(object_creators, ObjectCreatorsAdmin)
admin.site.register(loot_list, LootListAdmin)
admin.site.register(common_objects, CommonObjectsAdmin)
admin.site.register(equipment_types, EquipmentTypesAdmin)
admin.site.register(equipment_positions, EquipmentPositionsAdmin)
admin.site.register(equipments, EquipmentsAdmin)
admin.site.register(character_careers, CharacterCareersAdmin)
admin.site.register(career_equipments, CareersEquipmentsAdmin)
admin.site.register(character_models, CharacterModelsAdmin)
admin.site.register(world_npcs, WorldNPCAdmin)
admin.site.register(common_characters, CommonCharactersAdmin)
admin.site.register(skills, SkillsAdmin)
admin.site.register(default_skills, DefaultSkillsAdmin)
admin.site.register(quests, QuestsAdmin)
admin.site.register(quest_objective_types, QuestObjectiveTypesAdmin)
admin.site.register(quest_objectives, QuestObjectivesAdmin)
admin.site.register(quest_dependency_types, QuestDependencyTypesAdmin)
admin.site.register(quest_dependencies, QuestDependenciesAdmin)
admin.site.register(event_data, EventDataAdmin)
admin.site.register(dialogues, DialoguesAdmin)
admin.site.register(dialogue_relations, DialogueRelationsAdmin)
admin.site.register(dialogue_sentences, DialogueSentencesAdmin)
admin.site.register(npc_dialogues, NPCDialoguesAdmin)
admin.site.register(dialogue_quest_dependency, DialogueQuestDependencyAdmin)
admin.site.register(event_mobs, EventMobsAdmin)
admin.site.register(event_dialogues, EventDialoguesAdmin)
admin.site.register(localized_strings, LocalizedStringsAdmin)

