"""
Upgrade custom's game dir to the latest version.
"""

from muddery.server.upgrader.base_upgrader import BaseUpgrader
from muddery.utils.exception import MudderyError, ERR


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.4.1 (include this version)
    from_min_version = (0, 4, 1)

    # from max version 0.4.2 (not include this version)
    from_max_version = (0, 4, 2)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        pass

    def upgrade_data(self, data_path, game_template, muddery_lib):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        pass
