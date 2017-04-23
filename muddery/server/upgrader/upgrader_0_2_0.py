"""
Upgrade custom's game dir to the latest version.
"""

from __future__ import print_function

import os
import django.core.management
from evennia.server.evennia_launcher import init_game_directory
from muddery.server.upgrader.base_upgrader import BaseUpgrader


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from version 0.2.0
    from_version = (0, 2, 0)

    # to version 0.2.1
    to_version = (0, 2, 1)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
        """
        print("Upgrading game %s." % game_dir)

        os.chdir(game_dir)
        init_game_directory(game_dir, check_db=False)

        # make new migrations
        django_args = ["makemigrations"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["migrate"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

    def upgrade_data(self, data_path, game_template):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
        """
        pass
