"""
Upgrade custom's game dir to the latest version.
"""

from __future__ import print_function

import os
import muddery
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
            print("\nCan not find dir '%s'.\n" % game_dir)
            return
            
        if self.is_running(game_dir):
            print("\nThe game is still running, stop it first.\n")
            return
        
        game_ver = ""
        try:
            with open(os.path.join(game_dir, "muddery_version.txt"), 'r') as f:
                game_ver = f.read().strip()
        except Exception, e:
            pass
        game_ver = utils.version_to_num(game_ver)
            
        print("Game version: %s" % (game_ver,))

        upgraded = False

        # Get proper upgrader.
        try:
            for upgrader in self.upgrader_list:
                if upgrader.can_upgrade(game_ver):
                    # backup current game dir
                    utils.make_backup(game_dir)

                    # do upgrade
                    upgrader.upgrade(game_dir, game_template)
                    upgraded = True
                    break

            if upgraded:
                print("\nYour game has been upgraded to muddery version %s.\n" % muddery.__version__)
            else:
                print("\nYour game does not need upgrade.\n")

        except Exception, e:
            print("\nUpgrade failed: %s\n" % e)

        return
        
    def is_running(self, game_dir):
        """
        Check whether the game server is running.
        """
        server_pidfile = os.path.join(game_dir, "server", "server.pid")
        portal_pidfile = os.path.join(game_dir, "server", "portal.pid")
        
        return os.path.exists(server_pidfile) or os.path.exists(portal_pidfile)

UPGRADE_HANDLER = UpgradeHandler()
