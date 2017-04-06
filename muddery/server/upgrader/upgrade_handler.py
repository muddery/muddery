"""
Upgrade custom's game dir to the latest version.
"""

from __future__ import print_function

import os
from muddery.server.upgrader import utils
from muddery.server.upgrader import upgrader_0_0


class UpgradeHandler(object):
    """
    Upgrade custom's game dir to the latest version.
    """
    def __init__(self):
        """
        Add upgraders.
        """
        self.upgrader_list = []
        self.upgrader_list.append(upgrader_0_0.Upgrader())

    def upgrade(self, game_dir, game_template):
        # Get first two version numbers.
        if not os.path.exists(game_dir):
            print("Can not find dir '%s'" % game_dir)
        
        game_ver = ""
        try:
            with open(os.path.join(game_dir, "muddery_version.txt"), 'r') as f:
                game_ver = f.read().strip()
        except Exception, e:
            pass
        game_ver = utils.version_to_num(game_ver)
            
        print("Game version: %s" % (game_ver,))
        
        if not self.upgrader_list:
            print("Does not need upgrade.")
            return

        # Get proper upgrader.
        for upgrader in self.upgrader_list:
            if upgrader.can_upgrade(game_ver):
                # backup current game dir
                utils.make_backup(game_dir)
                
                # do upgrade
                upgrader.upgrade(game_dir, game_template)
                break

        print("Upgraded.")
        return

UPGRADE_HANDLER = UpgradeHandler()
