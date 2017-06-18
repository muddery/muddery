from django.contrib import admin

# Register your models here.


class GameSettingsAdmin(admin.ModelAdmin):
    list_display = ('connection_screen',
                    'global_cd',
                    'auto_cast_skill_cd',
                    'can_give_up_quests',
                    'can_close_dialogue',
                    'single_dialogue_sentence',
                    'auto_resume_dialogues',
                    'default_home_key',
                    'start_location_key',
                    'default_player_home_key',
                    'default_player_character_key',
                    'map_scale',
                    'map_room_size',)


class ClassCategoriesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'desc')


class TypeclassesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'path',
                    'category',
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


class TwoWayExitsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'reverse_name')


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


class LootListAdmin(admin.ModelAdmin):
    list_display = ('provider',
                    'object',
                    'number',
                    'odds',
                    'quest',
                    'condition')


class CreatorLootListAdmin(LootListAdmin):
    pass


class CharacterLootListAdmin(LootListAdmin):
    pass


class QuestRewardListAdmin(LootListAdmin):
    pass


class CommonObjectsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'max_stack',
                    'unique')


class FoodsAdmin(CommonObjectsAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'max_stack',
                    'unique',
                    'position',
                    'type',
                    'hp',
                    'mp')


class EquipmentTypesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'desc')


class EquipmentPositionsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'desc')


class EquipmentsAdmin(CommonObjectsAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'max_stack',
                    'unique',
                    'position',
                    'type',
                    'attack',
                    'defence')


class CharacterCareersAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'desc')


class CareersEquipmentsAdmin(admin.ModelAdmin):
    list_display = ('career',
                    'equipment')


class CharacterModelsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'level',
                    'max_exp',
                    'max_hp',
                    'max_mp',
                    'attack',
                    'defence',
                    'give_exp')


class WorldNPCAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'location',
                    'model',
                    'level',
                    'condition')


class CommonCharactersAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'model',
                    'level')


class SkillsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'cd',
                    'passive',
                    'condition',
                    'function')


class DefaultSkillsAdmin(admin.ModelAdmin):
    list_display = ('character',
                    'skill')


class QuestsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'condition',
                    'action')


class QuestObjectiveTypesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'type_id',
                    'name',
                    'desc')


class QuestObjectivesAdmin(admin.ModelAdmin):
    list_display = ('quest',
                    'ordinal',
                    'type',
                    'object',
                    'number',
                    'desc')


class QuestDependencyTypesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'type_id',
                    'name',
                    'desc')


class QuestDependenciesAdmin(admin.ModelAdmin):
    list_display = ('quest',
                    'dependency',
                    'type')


class EventTypesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'type_id',
                    'name',
                    'desc')


class EventTriggerTypesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'type_id',
                    'name',
                    'desc')


class EventDataAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'type',
                    'trigger_type',
                    'trigger_obj',
                    'condition')


class DialoguesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'condition')


class DialogueQuestDependenciesAdmin(admin.ModelAdmin):
    list_display = ('dialogue',
                    'dependency',
                    'type')


class DialogueRelationsAdmin(admin.ModelAdmin):
    list_display = ('dialogue',
                    'next_dlg')


class DialogueSentencesAdmin(admin.ModelAdmin):
    list_display = ('dialogue',
                    'ordinal',
                    'speaker',
                    'content',
                    'action',
                    'provide_quest',
                    'complete_quest')


class NPCDialoguesAdmin(admin.ModelAdmin):
    list_display = ('npc',
                    'dialogue',
                    'default')


class EventAttacksAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'mob',
                    'level',
                    'odds',
                    'desc')


class EventDialoguesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'dialogue',
                    'npc')


class LocalizedStringsAdmin(admin.ModelAdmin):
    list_display = ('origin',
                    'local')


class ImageResourcesAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'resource')
