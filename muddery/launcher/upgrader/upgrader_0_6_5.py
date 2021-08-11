"""
Upgrade custom's game dir to the latest version.
"""

import traceback
import os
import shutil
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
        # copy typeclass path
        source_path = os.path.join(muddery_lib, "game_templates", game_template, "elements")
        target_path = os.path.join(game_dir, "elements")
        shutil.copytree(source_path, target_path)

        # copy model files
        gamedata_model_old = os.path.join(game_dir, "gamedata", "models.py")
        gamedata_model_bak = os.path.join(game_dir, "gamedata", "models_bak.py")
        gamedata_model_default = os.path.join(muddery_lib, "game_templates", "default", "gamedata", "models.py")
        gamedata_model_new = os.path.join(muddery_lib, "game_templates", game_template, "gamedata", "models.py")
        os.rename(gamedata_model_old, gamedata_model_bak)
        shutil.copyfile(gamedata_model_default, gamedata_model_old)
        try:
            shutil.copyfile(gamedata_model_new, gamedata_model_old)
        except FileNotFoundError:
            pass

        worlddata_model_old = os.path.join(game_dir, "worlddata", "models.py")
        worlddata_model_bak = os.path.join(game_dir, "worlddata", "models_bak.py")
        worlddata_model_default = os.path.join(muddery_lib, "game_templates", "default", "worlddata", "models.py")
        worlddata_model_new = os.path.join(muddery_lib, "game_templates", game_template, "worlddata", "models.py")
        os.rename(worlddata_model_old, worlddata_model_bak)
        shutil.copyfile(worlddata_model_default, worlddata_model_old)
        try:
            shutil.copyfile(worlddata_model_new, worlddata_model_old)
        except FileNotFoundError:
            pass
        
        # init game dir
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
            "worlddata_action_room_interval",
            "worlddata_world_rooms",
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

        # make new migrations
        django_args = ["makemigrations", "gamedata"]
        django_kwargs = {}
        django.core.management.call_command(*django_args, **django_kwargs)

        django_args = ["migrate", "gamedata"]
        django_kwargs = {"database": "gamedata"}
        django.core.management.call_command(*django_args, **django_kwargs)

        # properties_dict
        #try:
        #    cursor.execute("""
        #        UPDATE worlddata_properties_dict
        #        SET element_type=(SELECT typeclass FROM worlddata_properties_dict_bak t1 WHERE worlddata_properties_dict.id=t1.id)
        #    """)
        #except Exception as e:
        #    print("properties_dict: %s" % e)

        # character_states_dict
        try:
            cursor.execute("""
                INSERT INTO worlddata_character_states_dict (key, name, `default`, desc)
                SELECT property, name, `default`, desc FROM worlddata_properties_dict_bak
                WHERE typeclass="CHARACTER" AND mutable=1
            """)
        except Exception as e:
            print("character_states_dict: %s" % e)

        # characters
        try:
            cursor.execute("""
                UPDATE worlddata_characters
                SET name=(SELECT name FROM worlddata_objects_bak t1 WHERE worlddata_characters.key=t1.key),
                element_type=(SELECT typeclass FROM worlddata_objects_bak t2 WHERE worlddata_characters.key=t2.key),
                desc=(SELECT desc FROM worlddata_objects_bak t3 WHERE worlddata_characters.key=t3.key)
            """)
        except Exception as e:
            print("characters: %s" % e)

        # world_rooms
        #try:
        #    cursor.execute("""
        #        UPDATE worlddata_world_rooms
        #        SET area=(SELECT location FROM worlddata_world_rooms_bak t1 WHERE worlddata_world_rooms.key=t1.key),
        #    """)
        #except Exception as e:
        #    print("characters: %s" % e)

        # common_objects
        try:
            cursor.execute("""
                INSERT INTO worlddata_common_objects (key, icon, name, element_type, desc)
                SELECT key, icon, '', '', '' FROM worlddata_world_objects_bak
            """)
        except Exception as e:
            print("common_objects: %s" % e)

        try:
            cursor.execute("""
                UPDATE worlddata_common_objects
                SET name=(SELECT name FROM worlddata_objects_bak t1 WHERE worlddata_common_objects.key=t1.key),
                element_type=(SELECT typeclass FROM worlddata_objects_bak t2 WHERE worlddata_common_objects.key=t2.key),
                desc=(SELECT desc FROM worlddata_objects_bak t3 WHERE worlddata_common_objects.key=t3.key)
            """)
        except Exception as e:
            print("common_objects: %s" % e)

        # element_properties
        try:
            cursor.execute("""
                INSERT INTO worlddata_element_properties (element, key, level, property, value)
                SELECT '', object, level, property, value FROM worlddata_object_properties_bak
            """)
        except Exception as e:
            print("element_properties: %s" % e)

        try:
            cursor.execute("""
                UPDATE worlddata_element_properties
                SET element=(
                    SELECT typeclass
                    FROM worlddata_objects_bak t1
                    WHERE worlddata_element_properties.key=t1.key)
            """)
        except Exception as e:
            print("element_properties: %s" % e)

        # pocket_objects
        try:
            cursor.execute("""
                INSERT INTO worlddata_pocket_objects (key, max_stack, `unique`, can_remove, can_discard)
                SELECT key, max_stack, `unique`, can_remove, can_discard FROM worlddata_common_objects_bak
            """)
        except Exception as e:
            print("pocket_objects: %s" % e)

        # profit_rooms
        try:
            cursor.execute("""
                INSERT INTO worlddata_profit_rooms (key, interval, offline, begin_message, end_message, condition)
                SELECT t1.trigger_obj, t2.interval, t2.offline, t2.begin_message, t2.end_message, ''
                FROM worlddata_event_data t1, worlddata_action_room_interval_bak t2
                WHERE t1.action='ACTION_ROOM_INTERVAL' and t1.key=t2.event_key
            """)
        except Exception as e:
            print("profit_rooms: %s" % e)

        # properties_dict
        try:
            cursor.execute("""
                DELETE FROM worlddata_properties_dict
                WHERE id IN (
                    SELECT t1.id FROM worlddata_properties_dict t1
                    INNER JOIN worlddata_properties_dict_bak t2
                        ON t1.element_type=t2.typeclass AND t1.property = t2.property
                    WHERE t2.mutable = 1)
            """)
        except Exception as e:
            print("properties_dict: %s" % e)

        # quests
        try:
            cursor.execute("""
                UPDATE worlddata_quests
                SET name=(SELECT name FROM worlddata_objects_bak t1 WHERE worlddata_quests.key=t1.key),
                desc=(SELECT desc FROM worlddata_objects_bak t3 WHERE worlddata_quests.key=t3.key)
            """)
        except Exception as e:
            print("quests: %s" % e)

        # room_profit_list
        try:
            cursor.execute("""
                INSERT INTO worlddata_room_profit_list (provider, object, level, number, odds, multiple, message, quest, condition)
                SELECT t1.trigger_obj, t3.object, t3.level, t3.number, t3.odds, t3.multiple, t3.message, '', ''
                FROM worlddata_event_data t1, worlddata_action_room_interval_bak t2, worlddata_action_get_objects t3
                WHERE t1.action='ACTION_ROOM_INTERVAL' AND t1.key=t2.event_key AND t2.action='ACTION_GET_OBJECTS'
                AND t2.event_key=t3.event_key
            """)
        except Exception as e:
            print("room_profit_list: %s" % e)

        # modify the setting file
        settings_old_path = os.path.join(game_dir, "server", "conf", "settings.py")
        settings_new_path = os.path.join(game_dir, "server", "conf", "new_settings.py")
        with open(settings_new_path, "w") as settings_new:
            with open(settings_old_path, "r") as settings_old:
                for line in settings_old.readlines():
                    if line.find("TYPECLASS") >= 0:
                        continue
                    settings_new.write(line)

        settings_bak_path = os.path.join(game_dir, "server", "conf", "settings_bak.py")
        os.rename(settings_old_path, settings_bak_path)
        os.rename(settings_new_path, settings_old_path)


