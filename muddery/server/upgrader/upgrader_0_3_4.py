"""
Upgrade custom's game dir to the latest version.
"""

from __future__ import print_function

import os, ast, json
import django.core.management
from evennia.server.evennia_launcher import init_game_directory
from muddery.server.upgrader.base_upgrader import BaseUpgrader
from django.apps import apps


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.0.0 (include this version)
    from_min_version = (0, 2, 10)

    # from max version 0.3.3 (not include this version)
    from_max_version = (0, 3, 3)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        os.chdir(game_dir)
        init_game_directory(game_dir, check_db=False)

        # make new migrations
        django_args = ["makemigrations"]
        django_kwargs = {"database": "worlddata"}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["migrate"]
        django_kwargs = {"database": "worlddata"}
        django.core.management.call_command(*django_args, **django_kwargs)

        from django.conf import settings

        game_settings = apps.get_model(settings.WORLD_DATA_APP, "game_settings")
        record = game_settings.objects.first()
        map_scale = record.map_scale
        room_size = record.map_room_size

        world_areas = apps.get_model(settings.WORLD_DATA_APP, "world_areas")
        world_rooms = apps.get_model(settings.WORLD_DATA_APP, "world_rooms")

        areas = world_areas.objects.all()
        for area in areas:
            min_x = 0
            max_x = 0
            min_y = 0
            max_y = 0
            rooms = world_rooms.objects.filter(location=area)
            for room in rooms:
                position = room.position
                if position:
                    position = ast.literal_eval(position)
                    x = position[0]
                    y = position[1]
                    if x > max_x:
                        max_x = x
                    if y > max_y:
                        max_y = y
                    if x < min_x:
                        min_x = x
                    if y < min_y:
                        min_y = y

            shift_x = min_x * map_scale + room_size
            shift_y = max_y * map_scale + room_size

            for room in rooms:
                position = room.position
                if position:
                    position = ast.literal_eval(position)
                    x = position[0]
                    y = position[1]

                    x = x * map_scale + shift_x
                    y = -y * map_scale + shift_y
                    record.position = json.dumps([x, y])
                    record.save()


    def upgrade_data(self, data_path, game_template, muddery_lib):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        pass
