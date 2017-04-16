"""
Upgrade custom's game dir to the latest version.
"""


class BaseUpgrader(object):
    """
    Upgrade a game dir from the version in [<from_version>, <to_version>) to version
    <target_version>.
    """
    # upgrade from version from_version to to_version
    # from version 0.0
    from_version = (0, 0)
    
    # NOT include this version
    # to version 0.0
    to_version = (0, 0)

    # Upgrade to the target version. None means the latest version.
    target_version = None
    
    def upgrade(self, game_dir, game_template):
        """
        Do upgrade.
        """
        pass
        
    def can_upgrade(self, game_ver):
        """
        game_version: (list)version numbers.
        """
        if game_ver[0] < self.from_version[0]:
            return False
        elif game_ver[0] == self.from_version[0] and game_ver[1] < self.from_version[1]:
            return False
        elif game_ver[0] > self.to_version[0]:
            return False
        elif game_ver[0] == self.to_version[0] and game_ver[1] >= self.to_version[1]:
            return False
        else:
            return True
