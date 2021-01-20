"""
Upgrade custom's game dir to the latest version.
"""

import traceback
import os
import django.core.management
from evennia.server.evennia_launcher import init_game_directory
from muddery.launcher.upgrader.base_upgrader import BaseUpgrader
from muddery.launcher.upgrader.utils import file_append
from muddery.launcher.utils import import_system_data
from muddery.server.utils.exception import MudderyError, ERR


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.6.2 (include this version)
    from_min_version = (0, 6, 2)

    # from max version 0.6.4 (not include this version)
    from_max_version = (0, 6, 4)

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

        # add honour_settings table to the worlddata model
        file_path = os.path.join(game_dir, "worlddata", "models.py")
        file_append(file_path, [
            "\n",
            "class honour_settings(BaseModels.honour_settings):\n",
            "    pass\n",
            "\n"
        ])

        # add honours table to the gamedata model
        file_path = os.path.join(game_dir, "gamedata", "models.py")
        file_append(file_path, [
            "from muddery.server.database import gamedata_models as BaseModels",
            "\n",
            "class honours(BaseModels.honours):\n",
            "    pass\n",
            "\n"
        ])

        init_game_directory(game_dir, check_db=False)

        # make new migrations
        django_args = ["makemigrations", "worlddata"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["migrate", "worlddata"]
        django_kwargs = {"database": "worlddata"}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["makemigrations", "gamedata"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["migrate", "gamedata"]
        django_kwargs = {"database": "gamedata"}
        django.core.management.call_command(*django_args, **django_kwargs)

        # load system data
        try:
            import_system_data()
            print("Import system data success.")
        except Exception as e:
            traceback.print_exc()
            raise

    def upgrade_data(self, data_path, game_template, muddery_lib):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        pass
