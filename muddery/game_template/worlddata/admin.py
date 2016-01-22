from django.contrib import admin

from form import *
from models import *
from muddery.worlddata import admin_base


# Register your models here.


class TypeclassesAdmin(admin_base.TypeclassesAdmin):
    pass


class WorldRoomsAdmin(admin_base.WorldRoomsAdmin):
    pass


class WorldExitsAdmin(admin_base.WorldExitsAdmin):
    pass


class ExitLocksAdmin(admin_base.ExitLocksAdmin):
    form = ExitLocksForm


class WorldObjectsAdmin(admin_base.WorldObjectsAdmin):
    pass


class ObjectCreatorsAdmin(admin_base.ObjectCreatorsAdmin):
    form = ObjectCreatorsForm


class LootListAdmin(admin_base.LootListAdmin):
    form = LootListForm


class CommonObjectsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'max_stack',
                    'unique',
                    'effect')


class EquipmentTypesAdmin(admin.ModelAdmin):
    list_display = ('type',
                    'name',
                    'desc',
                    'career')


class EquipmentsAdmin(admin.ModelAdmin):
    list_display = ('position',
                    'type',
                    'attack',
                    'defence')


class WorldNPCAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'location',
                    'model',
                    'condition')
    form = WorldNPCForm


class CommonCharactersAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'model')
    form = CommonCharactersForm


class SkillsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'cd',
                    'passive',
                    'condition',
                    'function',
                    'effect')


class QuestsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'condition',
                    'action')


class QuestObjectivesAdmin(admin.ModelAdmin):
    list_display = ('get_quest',
                    'ordinal',
                    'type',
                    'object',
                    'number',
                    'desc')
    def get_quest(self, obj):
        return obj.quest.key
    form = QuestObjectivesForm


class QuestDependencyAdmin(admin.ModelAdmin):
    list_display = ('get_quest',
                    'get_dependency',
                    'type')
    def get_quest(self, obj):
        return obj.quest.key
    def get_dependency(self, obj):
        if obj.dependency:
            return obj.dependency.key
    form = QuestDependencyForm


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


class CharacterSkillsAdmin(admin.ModelAdmin):
    list_display = ('character',
                    'get_skill')

    def get_skill(self, obj):
        return obj.skill.key

    form = CharacterSkillsForm


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


admin.site.register(typeclasses, TypeclassesAdmin)
admin.site.register(world_rooms, WorldRoomsAdmin)
admin.site.register(world_exits, WorldExitsAdmin)
admin.site.register(exit_locks, ExitLocksAdmin)
admin.site.register(world_objects, WorldObjectsAdmin)
admin.site.register(object_creators, ObjectCreatorsAdmin)
admin.site.register(loot_list, LootListAdmin)
admin.site.register(common_objects, CommonObjectsAdmin)
admin.site.register(equipment_types, EquipmentTypesAdmin)
admin.site.register(equipments, EquipmentsAdmin)
admin.site.register(world_npcs, WorldNPCAdmin)
admin.site.register(common_characters, CommonCharactersAdmin)
admin.site.register(skills, SkillsAdmin)
admin.site.register(quests, QuestsAdmin)
admin.site.register(quest_objectives, QuestObjectivesAdmin)
admin.site.register(quest_dependency, QuestDependencyAdmin)
admin.site.register(event_data, EventDataAdmin)
admin.site.register(dialogues, DialoguesAdmin)
admin.site.register(dialogue_relations, DialogueRelationsAdmin)
admin.site.register(dialogue_sentences, DialogueSentencesAdmin)
admin.site.register(npc_dialogues, NPCDialoguesAdmin)
admin.site.register(dialogue_quest_dependency, DialogueQuestDependencyAdmin)
admin.site.register(character_models, CharacterModelsAdmin)
admin.site.register(character_skills, CharacterSkillsAdmin)
admin.site.register(event_mobs, EventMobsAdmin)
admin.site.register(event_dialogues, EventDialoguesAdmin)
admin.site.register(localized_strings, LocalizedStringsAdmin)

