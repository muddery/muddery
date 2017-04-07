"""
Upgrade custom's game dir to the latest version.
"""

from __future__ import print_function

import os
import shutil
import django.core.management
from muddery.server.upgrader import utils
from muddery.server.upgrader.base_upgrader import BaseUpgrader


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    from_version = (0, 0)
    to_version = (0, 2)
    target_version = None
    
    def upgrade(self, game_dir, game_template):
        """
        Do upgrade.
        """
        print("Doing upgrade.")

        temp_dir = None
        try:
            # Move game dir to temp dir.
            temp_dir = utils.to_temp_dir(game_dir)

            # get settings
            setting_list = set(["ALLOWED_HOSTS",
                                "WEBSERVER_PORTS",
                                "WEBSOCKET_CLIENT_PORT",
                                "AMP_PORT",
                                "LANGUAGE_CODE",
                                "SECRET_KEY"])
            setting_dict = utils.get_settings(temp_dir, setting_list)

            # create new game
            utils.create_game(game_dir, game_template, setting_dict)
                    
            # copy old files
            # database
            utils.copy_path(temp_dir, game_dir, os.path.join("server", "muddery.db3"))

            # migrations
            utils.copy_path(temp_dir, game_dir, os.path.join("worlddata", "migrations"))

            # make new migrations
            os.chdir(game_dir)
            django_args = ["makemigrations"]
            django_kwargs = {}
            django.core.management.call_command(*django_args, **django_kwargs)

            django_args = ["migrate"]
            django_kwargs = {}
            django.core.management.call_command(*django_args, **django_kwargs)
            
            # copy game name
            server_name = utils.get_settings(temp_dir, ["SERVERNAME"])
            if server_name:
                kwargs = {"game_name": server_name["SERVERNAME"]}
                from muddery.worlddata.data_sets import DATA_SETS
                DATA_SETS.game_settings.objects.all().update(**kwargs)

        finally:
            if temp_dir:
                # remove temp dir
                shutil.rmtree(temp_dir)
