"""
Upgrade custom's game dir to the latest version.
"""

import traceback
import os
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
import django.core.management
from evennia.server.evennia_launcher import init_game_directory
from muddery.launcher.upgrader.base_upgrader import BaseUpgrader
from muddery.launcher.upgrader.utils import file_append
from muddery.launcher.utils import import_system_data
from muddery.server.utils.exception import MudderyError, ERR


class Upgrader(BaseUpgrader):
    """
    Upgrade a game dir to a specified version.
    """
    # Can upgrade the game of version between from_version and to_version.
    # from min version 0.6.4 (include this version)
    from_min_version = (0, 6, 4)

    # from max version 0.7.0 (not include this version)
    from_max_version = (0, 7, 0)

    target_version = None
    
    def upgrade_game(self, game_dir, game_template, muddery_lib):
        """
        Upgrade a game.

        Args:
            game_dir: (string) the game dir to be upgraded.
            game_template: (string) the game template used to upgrade the game dir.
            muddery_lib: (string) muddery's dir
        """
        os.chdir(game_dir)

        init_game_directory(game_dir, check_db=False)

        # copy current tables
        cursor = connections[settings.WORLD_DATA_APP].cursor()

        to_copy = [
            "worlddata_common_objects",
            "worlddata_object_properties",
            "worlddata_objects",
            "worlddata_world_objects",
            "worlddata_properties_dict",
        ]
        for table in to_copy:
            try:
                cursor.execute("CREATE TABLE %(table)s_bak AS SELECT * FROM %(table)s" % {"table": table})
            except OperationalError as e:
                print("%s: %s" % (type(e), e))

        # make new migrations
        django_args = ["makemigrations", "worlddata"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["migrate", "worlddata"]
        django_kwargs = {"database": "worlddata"}
        django.core.management.call_command(*django_args, **django_kwargs)

        # character_states_dict
        cursor.execute("""
            INSERT INTO worlddata_character_states_dict (key, name, `default`, desc)
            SELECT property, name, `default`, desc FROM worlddata_properties_dict_bak
            WHERE typeclass="CHARACTER" AND mutable=1
        """)
