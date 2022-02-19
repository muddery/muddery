"""
Upgrade custom's game dir to the latest version.
"""

from muddery.launcher.upgrader.base_upgrader import BaseUpgrader
from muddery.common.utils.exception import MudderyError, ERR


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.6.4 (include this version)
    from_min_version = (0, 7, 0)

    # from max version 0.7.0 (not include this version)
    from_max_version = (0, 8, 0)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        print("""
    您好，由于此次版本更新的内容过多，无法自动从旧版本升级到新版本。
    请创建新的python虚拟环境（需要python3.9或以上版本），获取最新代码，
    并重新安装游戏。
        
        """)

        raise MudderyError(ERR.can_not_upgrade, "You should upgrade the game manually.")
