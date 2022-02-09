"""
Upgrade custom's game dir to the latest version.
"""

import os
import django.core.management
from evennia.server.evennia_launcher import init_game_directory
from muddery.launcher.upgrader.base_upgrader import BaseUpgrader


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.4.1 (include this version)
    from_min_version = (0, 4, 1)

    # from max version 0.5.1 (not include this version)
    from_max_version = (0, 5, 3)

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
        django_args = ["makemigrations", "worlddata"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["migrate", "worlddata"]
        django_kwargs = {"database": "worlddata"}
        django.core.management.call_command(*django_args, **django_kwargs)

        # load system localized strings
        from django.conf import settings
        from muddery.server.utils import importer

        # system data file's path
        system_data_path = os.path.join(settings.MUDDERY_DIR, settings.WORLD_DATA_FOLDER)

        # localized string file's path
        system_localized_string_path = os.path.join(system_data_path,
                                                    settings.LOCALIZED_STRINGS_FOLDER,
                                                    settings.LANGUAGE_CODE)

        # load data
        importer.import_table_path(system_localized_string_path, settings.LOCALIZED_STRINGS_MODEL)

    def upgrade_data(self, data_path, game_template, muddery_lib):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        pass
