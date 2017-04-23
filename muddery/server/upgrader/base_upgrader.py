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
    # from version 0.0.0
    from_version = (0, 0, 0)
    
    # NOT include this version
    # to version 0.0.0
    to_version = (0, 0, 0)

    # Upgrade to the target version. None means the latest version.
    target_version = None
    
    def upgrade_game(self, game_dir, game_template):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
        """
        pass

    def upgrade_data(self, data_path, game_template):
        """
        Upgrade game data.

        Args:
            data_path: (string) the data path to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
        """
        pass
        
    def can_upgrade(self, game_ver):
        """
        game_version: (list)version numbers.
        """
        # The game version should be equal or bigger than from_version.
        if compare_version(game_ver, self.from_version) == -1:
            return False

        # The game version should be smaller than to_version.
        if compare_version(game_ver, self.to_version) != -1:
            return False

        return True
