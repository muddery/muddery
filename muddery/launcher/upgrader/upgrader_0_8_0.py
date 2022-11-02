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
    from_min_version = (0, 8, 0)

    # from max version 0.8.1 (not include this version)
    from_max_version = (0, 8, 1)

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
    您好，由于此次版本更新的内容过多，自动升级时之前版本的玩家数据无法保留，
    游戏目录中的文件会被覆盖。

            """)

        answer = input("    您是否要继续？（Y/N）")
        if answer.lower() != "y":
            raise MudderyError(ERR.can_not_upgrade, "用户选择退出。")

        # copy model files
        gamedata_model_old = os.path.join(game_dir, "gamedata", "models.py")
        gamedata_model_default = os.path.join(muddery_lib, "game_templates", "default", "gamedata", "models.py")
        shutil.copyfile(gamedata_model_default, gamedata_model_old)

        if game_template:
            gamedata_model_new = os.path.join(muddery_lib, "game_templates", game_template, "gamedata", "models.py")
            try:
                shutil.copyfile(gamedata_model_new, gamedata_model_old)
            except FileNotFoundError:
                pass

        if game_template == "example_cn":
            file_old = os.path.join(game_dir, "elements", "character.py")
            file_new = os.path.join(muddery_lib, "game_templates", game_template, "elements", "character.py")
            shutil.copyfile(file_new, file_old)

            file_old = os.path.join(game_dir, "elements", "player_character.py")
            file_new = os.path.join(muddery_lib, "game_templates", game_template, "elements", "player_character.py")
            shutil.copyfile(file_new, file_old)

        from muddery.launcher import manager

        # remove gamedata
        gamedata_old = os.path.join(game_dir, "server", "gamedata.db3")
        gamedata_bak = os.path.join(game_dir, "server", "gamedata_bak.db3")
        try:
            os.rename(gamedata_old, gamedata_bak)
            manager.create_server_tables()
        except:
            print("""
    无法自动删除玩家数据，请自行删除。

            """)

        manager.migrate_database("worlddata")
        manager.collect_webclient_static()
        manager.collect_worldeditor_static()
