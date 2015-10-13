from django.contrib import admin
from models import world_rooms, world_exits, world_objects, world_npcs

# Register your models here.

class WorldRoomsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'location',
                    'home',
                    'lock')


class WorldExitsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'location',
                    'home',
                    'lock',
                    'destination')


class WorldObjectsAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'location',
                    'home',
                    'lock')


class WorldNPCAdmin(admin.ModelAdmin):
    list_display = ('key',
                    'name',
                    'typeclass',
                    'desc',
                    'location',
                    'home',
                    'dialogue',
                    'lock')


admin.site.register(world_rooms, WorldRoomsAdmin)
admin.site.register(world_exits, WorldExitsAdmin)
admin.site.register(world_objects, WorldObjectsAdmin)
admin.site.register(world_npcs, WorldNPCAdmin)
