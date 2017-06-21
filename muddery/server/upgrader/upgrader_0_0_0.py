"""
Upgrade custom's game dir to the latest version.
"""

from __future__ import print_function

import os
import shutil
import ast
import glob
import django.core.management
from muddery.server.upgrader import utils
from muddery.server.upgrader.base_upgrader import BaseUpgrader


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.0.0 (include this version)
    from_min_version = (0, 0, 0)

    # from max version 0.2.0 (not include this version)
    from_max_version = (0, 2, 0)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        print("Upgrading game 0.0.0-0.2.0 %s." % game_dir)

        temp_dir = None
        try:
            # get settings
            setting_list = {"ALLOWED_HOSTS",
                            "WEBSERVER_PORTS",
                            "WEBSOCKET_CLIENT_PORT",
                            "AMP_PORT",
                            "LANGUAGE_CODE",
                            "SECRET_KEY"}
            setting_dict = utils.get_settings(game_dir, setting_list)

            # create new game in temp dir
            temp_dir = utils.get_temp_dir_name(game_dir)
            utils.create_game(temp_dir, game_template, setting_dict)

            # copy old files
            # database
            utils.copy_path(game_dir, temp_dir, os.path.join("server", "muddery.db3"))

            # migrations
            shutil.rmtree(os.path.join(temp_dir, "worlddata", "migrations"))
            utils.copy_path(game_dir, temp_dir, os.path.join("worlddata", "migrations"))

            # make new migrations
            os.chdir(temp_dir)
            django_args = ["makemigrations"]
            django_kwargs = {}
            django.core.management.call_command(*django_args, **django_kwargs)

            django_args = ["migrate"]
            django_kwargs = {}
            django.core.management.call_command(*django_args, **django_kwargs)
            
            # copy game name
            from muddery.worlddata.data_sets import DATA_SETS
            server_name = utils.get_settings(temp_dir, ["SERVERNAME"])
            if server_name:
                kwargs = {"game_name": ast.literal_eval(server_name["SERVERNAME"])}
                DATA_SETS.game_settings.objects.all().update(**kwargs)

            # upgrade system data
            from django.conf import settings
            custom_data_path = os.path.join(game_dir, settings.WORLD_DATA_FOLDER)
            system_data_path = os.path.join(settings.MUDDERY_DIR, settings.WORLD_DATA_FOLDER)

            for data_handler in DATA_SETS.system_data:
                data_handler.clear_model_data(system_data=False)
                try:
                    data_handler.import_from_path(custom_data_path, system_data=False)
                except Exception, e:
                    print("Cannot import game data. %s" % e)

                data_handler.clear_model_data(system_data=True)
                try:
                    data_handler.import_from_path(system_data_path, system_data=True)
                except Exception, e:
                    print("Cannot import game data. %s" % e)

            # set shop goods' key
            for data in DATA_SETS.shop_goods.objects.all():
                data.full_clean()
                data.save()

            # clear web dir
            shutil.rmtree(os.path.join(game_dir, "web"))

            # copy temp dir to game dir
            utils.copy_tree(temp_dir, game_dir)

        finally:
            if temp_dir:
                # remove temp dir
                shutil.rmtree(temp_dir)

    def upgrade_data(self, data_path, game_template, muddery_lib):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        print("Upgrading game data 0.0.0-0.2.0 %s." % data_path)

        from muddery.worlddata.data_sets import DATA_SETS
        file_names = glob.glob(os.path.join(data_path, DATA_SETS.typeclasses.model_name + ".*"))
        for file_name in file_names:
            print("Remove file %s." % file_name)
            os.remove(file_name)
