from django.contrib import admin

from muddery.worlddata.form_base import *


# Register your models here.


class TypeclassesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'path',
                    'desc')


class WorldRoomsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'position')


class WorldExitsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'location',
                    'destination',
                    'condition')


class ExitLocksAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'unlock_condition',
                    'unlock_verb',
                    'locked_desc',
                    'auto_unlock')


class WorldObjectsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'location',
                    'condition')


class ObjectCreatorsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'loot_verb',
                    'loot_condition')


class ObjectLootListAdmin(admin.ModelAdmin):
    list_display = ('provider',
                    'object',
                    'number',
                    'odds',
                    'quest',
                    'condition')
    form = ObjectLootListForm


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
