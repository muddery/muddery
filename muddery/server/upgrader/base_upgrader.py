"""
Upgrade custom's game dir to the latest version.
"""


class BaseUpgrader(object):
    """
    Upgrade a game dir from the version in [<from_version>, <to_version>) to version
    <target_version>.
    """
    # include from_version
    from_version = (0, 0)
    
    # NOT include to_version
    to_version = (0, 0)

    # Upgrade to the target version. None means the latest version.
    target_version = None
    
    def upgrade(self, game_dir):
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
        elif game_ver[0] == self.to_version[0] and game_ver[1] > self.to_version[1]:
            return False
        else:
            return True
