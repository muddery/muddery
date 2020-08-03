"""
Upgrade custom's game dir to the latest version.
"""

import os
import django.core.management
from evennia.server.evennia_launcher import init_game_directory
from muddery.launcher.upgrader.base_upgrader import BaseUpgrader
from muddery.server.utils.exception import MudderyError, ERR
from muddery.muddery_launcher import import_local_data


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.6.1 (include this version)
    from_min_version = (0, 6, 1)

    # from max version 0.6.2 (not include this version)
    from_max_version = (0, 6, 2)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        print("""
    To upgrade the game, you can do these:
    
    1. To upgrade the libs, move to the Muddery source code's parent path and run:
       pip install --upgrade -e muddery
    2. To upgrade the database, move to the game path and run:
       muddery makemigrations
       muddery migrate
    3. Edit the game.cfg file, set the version to 0.6.2
        """)

        raise MudderyError(ERR.can_not_upgrade, "Can not upgrade.")

    def upgrade_data(self, data_path, game_template, muddery_lib):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        pass
