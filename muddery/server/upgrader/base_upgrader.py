"""
Upgrade custom's game dir to the latest version.
"""

from utils import compare_version


class BaseUpgrader(object):
    """
    Upgrade a game dir from the version in [<from_version>, <to_version>) to version
    <target_version>.
    """
    # Can upgrade the game of version between from_version and to_version.
    # min version 0.0.0 (include this version)
    from_min_version = (0, 0, 0)
    
    # from max version 0.0.0 (not include this version)
    from_max_version = (0, 0, 0)

    # Upgrade to the target version. None means the latest version.
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
        
    def can_upgrade(self, game_ver):
        """
        game_version: (list)version numbers.
        """
        # The game version should be equal or bigger than from_min_version.
        if compare_version(game_ver, self.from_min_version) == -1:
            return False

        # The game version should be smaller than from_max_version.
        if compare_version(game_ver, self.from_max_version) != -1:
            return False

        return True
