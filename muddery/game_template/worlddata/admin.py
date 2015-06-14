from django.contrib import admin
from models import world_rooms, world_exits, world_objects, world_npcs, dialogues

# Register your models here.

class WorldRoomsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'alias',
                    'typeclass',
                    'desc',
                    'location',
                    'home',
                    'lock',
                    'attributes')


class WorldExitsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'alias',
                    'typeclass',
                    'desc',
                    'location',
                    'home',
                    'lock',
                    'attributes',
                    'destination')


class WorldObjectsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'alias',
                    'typeclass',
                    'desc',
                    'location',
                    'home',
                    'lock',
                    'attributes')


class WorldNPCAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'alias',
                    'typeclass',
                    'desc',
                    'location',
                    'home',
                    'dialogue',
                    'lock',
                    'attributes')


class WorldDialogueAdmin(admin.ModelAdmin):
    list_display = ('dialogue',
                    'sentence',
                    'speaker',
                    'content',
                    'next',
                    'condition',
                    'action')


admin.site.register(world_rooms, WorldRoomsAdmin)
admin.site.register(world_exits, WorldExitsAdmin)
admin.site.register(world_objects, WorldObjectsAdmin)
admin.site.register(world_npcs, WorldNPCAdmin)
admin.site.register(dialogues, WorldDialogueAdmin)
