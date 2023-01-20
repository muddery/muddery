"""
Upgrade custom's game dir to the latest version.
"""

import os
import shutil
from muddery.launcher.upgrader.base_upgrader import BaseUpgrader
from muddery.common.utils.exception import MudderyError, ERR


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.8.0 (include this version)
    from_min_version = (0, 8, 1)

    # from max version 0.8.1 (not include this version)
    from_max_version = (0, 8, 2)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        # copy runner files
        file_old = os.path.join(game_dir, "run_server.py")
        file_new = os.path.join(muddery_lib, "game_templates", "default", "run_server.py")
        shutil.copyfile(file_new, file_old)

        file_old = os.path.join(game_dir, "run_webclient.py")
        file_new = os.path.join(muddery_lib, "game_templates", "default", "run_webclient.py")
        shutil.copyfile(file_new, file_old)

        file_old = os.path.join(game_dir, "run_worldeditor.py")
        file_new = os.path.join(muddery_lib, "game_templates", "default", "run_worldeditor.py")
        shutil.copyfile(file_new, file_old)

        print("""
        Game upgraded.
        
        Please GO TO the DIRECTORY where you place the Muddery source file and run:
        
            pip install --upgrade -e muddery
        
        to upgrade libs.

                """)
