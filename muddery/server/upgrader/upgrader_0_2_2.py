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


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.2.0 (include this version)
    from_min_version = (0, 2, 2)

    # from max version 0.2.2 (not include this version)
    from_max_version = (0, 2, 5)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        print("Upgrading game 0.2.2-0.2.4 %s." % game_dir)
        
        # add new models
        file_path = os.path.join(game_dir, "worlddata", "models.py")
                
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

        # add new forms
        file_path = os.path.join(game_dir, "worlddata", "forms.py")
        
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
