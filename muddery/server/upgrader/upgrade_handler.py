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

        # Get game version
        game_ver = utils.get_data_version(game_dir)
        print("Game version: %s" % (game_ver,))

        # Get proper upgrader.
        upgrader = self.get_upgrader(game_ver)
        if not upgrader:
            print("\nYour game does not need upgrade.\n")
            return

        try:
            # backup current game dir
            utils.make_backup(game_dir)

            # do upgrade
            upgrader.upgrade_game(game_dir, game_template)
            print("\nYour game has been upgraded to muddery version %s.\n" % muddery.__version__)

        except Exception, e:
            print("\nUpgrade failed: %s\n" % e)

        return

    def upgrade_data(self, data_path):
        """
        Upgrade game data.

        Args:
            data_path: (string) the path of game data.

        Returns:
            None
        """
        # Get game version
        game_ver = utils.get_data_version(data_path)
        print("Game data version: %s" % (game_ver,))

        # Get proper upgrader.
        upgrader = self.get_upgrader(game_ver)
        if not upgrader:
            # Does not need upgrade.
            return

        try:
            upgrader.upgrade_data(data_path, None)
            print("\nYour game data have been upgraded to muddery version %s.\n" % muddery.__version__)

        except Exception, e:
            print("\nUpgrade failed: %s\n" % e)

    def is_running(self, game_dir):
        """
        Check whether the game server is running.
        """
        server_pidfile = os.path.join(game_dir, "server", "server.pid")
        portal_pidfile = os.path.join(game_dir, "server", "portal.pid")
        
        return os.path.exists(server_pidfile) or os.path.exists(portal_pidfile)

    def get_upgrader(self, game_ver):
        """
        Get a proper upgrader according the data version.

        Args:
            game_ver: (tuple) version number's list.

        Returns:
            Game upgrader.
        """
        for upgrader in self.upgrader_list:
            if upgrader.can_upgrade(game_ver):
                return upgrader
        return None


UPGRADE_HANDLER = UpgradeHandler()
