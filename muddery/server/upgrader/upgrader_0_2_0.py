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


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.2.0 (include this version)
    from_min_version = (0, 2, 0)

    # from max version 0.2.2 (not include this version)
    from_max_version = (0, 2, 2)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        print("Upgrading game 0.2.0-0.2.2 %s." % game_dir)

        # comment out client_settings in models
        file_path = os.path.join(game_dir, "worlddata", "models.py")
        utils.comment_out_class(file_path, "client_settings")
        
        # add world_area to models
        utils.file_append(file_path, ["\n",
                                      "class world_areas(model_base.world_areas):\n",
                                      "    pass\n",
                                      "\n"])
                                      
        # add character_attributes_info to models
        utils.file_append(file_path, ["\n",
                                      "class character_attributes_info(model_base.character_attributes_info):\n",
                                      "    pass\n",
                                      "\n"])

        # add equipment_attributes_info to models
        utils.file_append(file_path, ["\n",
                                      "class equipment_attributes_info(model_base.equipment_attributes_info):\n",
                                      "    pass\n",
                                      "\n"])

        # add food_attributes_info to models
        utils.file_append(file_path, ["\n",
                                      "class food_attributes_info(model_base.food_attributes_info):\n",
                                      "    pass\n",
                                      "\n"])
                                      
        # comment out ClientSettingsForm in forms
        file_path = os.path.join(game_dir, "worlddata", "forms.py")
        utils.comment_out_class(file_path, "ClientSettingsForm")
        utils.comment_out_lines(file_path, ["Manager.init_data()"])
        
        # add world_area to forms
        utils.file_append(file_path, ["\n",
                                      "class WorldAreasForm(forms_base.WorldAreasForm):\n",
                                      "    pass\n",
                                      "\n"])
        
        # add character_attributes_info to forms       
        utils.file_append(file_path, ["\n",
                                      "class CharacterAttributesForm(forms_base.CharacterAttributesForm):\n",
                                      "    pass\n",
                                      "\n"])

        # add equipment_attributes_info to forms
        utils.file_append(file_path, ["\n",
                                      "class EquipmentAttributesForm(forms_base.EquipmentAttributesForm):\n",
                                      "    pass\n",
                                      "\n"])

        # add food_attributes_info to forms
        utils.file_append(file_path, ["\n",
                                      "class FoodAttributesForm(forms_base.FoodAttributesForm):\n",
                                      "    pass\n",
                                      "\n"])

        # add init method
        utils.file_append(file_path, ["\n",
                                      "Manager.init_data()\n",
                                      "\n"])
                                      
        # comment out ClientSettingsAdmin in admin
        file_path = os.path.join(game_dir, "worlddata", "admin.py")
        utils.comment_out_class(file_path, "ClientSettingsAdmin")
        utils.comment_out_lines(file_path, "admin.site.register(client_settings, ClientSettingsAdmin)")
        
        # update web folder
        shutil.rmtree(os.path.join(game_dir, "web"))
        
        default_template_dir = os.path.join(muddery_lib, "game_template")

        # update web folder
        utils.copy_path(default_template_dir, game_dir, "web")

        # update game editor
        utils.copy_path(default_template_dir, game_dir, os.path.join("worlddata", "editor"))
        
        if game_template:
            game_template_dir = os.path.join(configs.MUDDERY_TEMPLATE, game_template)

            # update web folder
            utils.copy_path(game_template_dir, game_dir, "web")

            # update statements
            utils.copy_path(game_template_dir, game_dir, "statements")

            # update web folder
            utils.copy_path(game_template_dir, game_dir, "web")

            # update game editor
            utils.copy_path(game_template_dir, game_dir, os.path.join("worlddata", "editor"))

            # template data
            utils.copy_path(game_template_dir, game_dir, os.path.join("worlddata", "data"))

        os.chdir(game_dir)
        init_game_directory(game_dir, check_db=False)

        # make new migrations
        django_args = ["makemigrations"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["migrate"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

        if game_template:
            # load custom attributes
            from muddery.worlddata.data_sets import DATA_SETS

            data_path = os.path.join(game_dir, "worlddata", "data")
            DATA_SETS.get_handler("character_attributes_info").import_from_path(data_path)
            DATA_SETS.get_handler("equipment_attributes_info").import_from_path(data_path)
            DATA_SETS.get_handler("food_attributes_info").import_from_path(data_path)

    def upgrade_data(self, data_path, game_template, muddery_lib):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        pass
