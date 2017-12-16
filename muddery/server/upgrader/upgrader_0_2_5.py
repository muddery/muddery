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
    # from min version 0.2.5 (include this version)
    from_min_version = (0, 2, 5)

    # from max version 0.2.6 (not include this version)
    from_max_version = (0, 2, 6)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        print("Upgrading game 0.2.5 %s." % game_dir)
        
        # add new models
        file_path = os.path.join(game_dir, "worlddata", "models.py")

        # add condition_desc to models
        utils.file_append(file_path, ["\n",
                                      "class condition_desc(model_base.condition_desc):\n",
                                      "    pass\n",
                                      "\n"])

        # add skill_types to models
        utils.file_append(file_path, ["\n",
                                      "class skill_types(model_base.skill_types):\n",
                                      "    pass\n",
                                      "\n"])

        # add honours to models
        utils.file_append(file_path, ["\n",
                                      "class honours(model_base.honours):\n",
                                      "    pass\n",
                                      "\n"])

        # add new forms
        file_path = os.path.join(game_dir, "worlddata", "forms.py")

        # move init to the end of the file
        utils.comment_out_lines(file_path, ["Manager.init_data()"])

        # add condition_desc to forms
        utils.file_append(file_path, ["\n",
                                      "class ConditionDescForm(forms_base.ConditionDescForm):\n",
                                      "    pass\n",
                                      "\n"])

        # add skill_types to forms
        utils.file_append(file_path, ["\n",
                                      "class SkillTypesForm(forms_base.SkillTypesForm):\n",
                                      "    pass\n",
                                      "\n"])

        # add init method
        utils.file_append(file_path, ["\n",
                                      "Manager.init_data()\n",
                                      "\n"])

        default_template_dir = os.path.join(muddery_lib, "game_template")

        # update game editor
        utils.copy_path(default_template_dir, game_dir, os.path.join("worlddata", "editor"))

        if game_template:
            game_template_dir = os.path.join(configs.MUDDERY_TEMPLATE, game_template)

            if game_template == "example_cn":
                # update AI
                utils.copy_path(game_template_dir, game_dir, "ai")

                # update settings file
                file_path = os.path.join(game_dir, "server", "conf", "settings.py")

                utils.file_append(file_path, ["\n",
                                              "AI_CHOOSE_SKILL = 'ai.choose_skill.ChooseSkill'\n",
                                              "\n"])

            if game_template == "legend":
                # update main.js
                utils.copy_path(game_template_dir, game_dir, os.path.join("web", "webclient_overrides", "webclient", "controllers", "main.js"))

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

        if game_template == "example_cn":
            # load data
            from muddery.worlddata.data_sets import DATA_SETS

            data_path = os.path.join(game_dir, "worlddata", "data")
            DATA_SETS.get_handler("skill_types").import_from_path(data_path)

    def upgrade_data(self, data_path, game_template, muddery_lib):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        pass
