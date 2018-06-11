"""
Upgrade custom's game dir to the latest version.
"""

from __future__ import print_function

import os
import shutil
import django.core.management
from evennia.server.evennia_launcher import init_game_directory
from muddery.server.upgrader.base_upgrader import BaseUpgrader
from muddery.server.upgrader import utils
from muddery.server.launcher import configs
from muddery.utils.exception import MudderyError


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.2.7 (include this version)
    from_min_version = (0, 2, 8)

    # from max version 0.2.7 (not include this version)
    from_max_version = (0, 2, 9)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        print("Upgrading game from version 0.2.8 %s." % game_dir)

        print("""
    We are very sorry that your game is too old to
    upgrade.

    If you want to upgrade your game nevertheless,
    please contact the author.""")

        raise MudderyError("Can not upgrade.")

        if game_template == "example_cn":
            game_template_dir = os.path.join(configs.MUDDERY_TEMPLATE, game_template)

            # copy webclient
            utils.copy_path(game_template_dir, game_dir, os.path.join("web", "webclient_overrides", "webclient"))

        os.chdir(game_dir)
        init_game_directory(game_dir, check_db=False)

        # make new migrations
        django_args = ["makemigrations"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["migrate"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

    def upgrade_data(self, data_path, game_template, muddery_lib):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        pass
