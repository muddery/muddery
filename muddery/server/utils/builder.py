"""
This module handles importing data from csv files and creating the whole game world from these data.
"""

import traceback
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import create, logger
from evennia.comms.models import ChannelDB
from muddery.server.utils import search
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.mappings.element_set import ELEMENT, ELEMENT_SET
from muddery.server.database.gamedata.object_keys import OBJECT_KEYS
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.world_areas import WorldAreas
from muddery.server.database.worlddata.world_rooms import WorldRooms
from muddery.server.database.worlddata.world_exits import WorldExits
from muddery.server.database.worlddata.world_npcs import WorldNPCs
from muddery.server.database.worlddata.world_objects import WorldObjects
from muddery.server.database.gamedata.player_character import PlayerCharacter
from muddery.server.database.gamedata.system_data import SystemData
from muddery.server.database.gamedata.character_location import CharacterLocation


def get_object_record(obj_key):
    """
    Query the object's record.

    Args:
        obj_key: (string) The key of the object.

    Returns:
        The object's data record.
    """
    record = None
    model_name = ELEMENT("OBJECT").model_name
    try:
        # Get record.
        record = WorldData.get_table_data(model_name, key=obj_key)
        record = record[0]
    except Exception as e:
        ostring = "Can not get record %s in %s: %s." % (obj_key, model_name, e)
        print(ostring)
        traceback.print_exc()

    return record


def build_object(obj_key, level=None, caller=None, reset_location=True):
    """
    Build objects of a model.

    Args:
        obj_key: (string) The key of the object.
        level: (number) The object's level.
        caller: (command caller) If provide, running messages will send to the caller.
    """

    # Get object's information
    record = None
    class_path = None
    try:
        model_name = ELEMENT("OBJECT").model_name

        try:
            # Get record.
            record = WorldData.get_table_data(model_name, key=obj_key)
            record = record[0]
        except Exception as e:
            ostring = "Can not get record %s in %s: %s." % (obj_key, model_name, e)
            print(ostring)
            traceback.print_exc()

        # get element model
        class_path = ELEMENT_SET.get_module(record.element_type)
    except Exception as e:
        ostring = "Can not get the element type of %s: %s." % (obj_key, e)
        print(ostring)
        traceback.print_exc()
        pass

    if not record or not class_path:
        ostring = "Can not find the data of %s." % obj_key
        print(ostring)
        traceback.print_exc()
        if caller:
            caller.msg(ostring)
        return

    # Create object.
    try:
        name = getattr(record, "name", "")
        obj = create.create_object(class_path, name)
    except Exception as e:
        ostring = "Can not create obj %s: %s" % (obj_key, e)
        print(ostring)
        traceback.print_exc()
        if caller:
            caller.msg(ostring)
        return

    try:
        # Set data info.
        obj.set_object_key(record.key, level=level, reset_location=reset_location)
    except Exception as e:
        ostring = "Can not set data info to obj %s: %s" % (obj_key, e)
        print(ostring)
        traceback.print_exc()
        if caller:
            caller.msg(ostring)
        return

    return obj


def build_unique_objects(objects_data, type_name, caller=None):
    """
    Build all objects in a model.

    Args:
        model_name: (string) The name of the data model.
        caller: (command caller) If provide, running messages will send to the caller.
    """
    # new objects
    new_obj_keys = set(record.key for record in objects_data)

    # current objects
    current_objs = OBJECT_KEYS.get_unique_objects(type_name)

    # remove objects
    count_remove = 0
    count_update = 0
    count_create = 0
    current_obj_keys = set()

    for obj_id, obj_key in current_objs.items():
        try:
            obj = search.get_object_by_id(obj_id)
        except Exception as e:
            logger.log_err("Can not get object: %s %s" % (obj_id, obj_key))
            continue

        if (obj_key in current_obj_keys) or (obj_key not in new_obj_keys):
            # This object is duplicated or should be remove.
            ostring = "Deleting %s" % obj_key
            print(ostring)
            if caller:
                caller.msg(ostring)

            # If default home will be removed, set default home to the Limbo.
            if ("#%s" % obj_id) == settings.DEFAULT_HOME:
                settings.DEFAULT_HOME = "#2"

            obj.delete()
            count_remove += 1
        else:
            try:
                # set data
                obj.load_data()
                # put obj to its default location
                obj.reset_location()
            except Exception as e:
                ostring = "%s can not load data:%s" % (obj.get_id(), e)
                print(ostring)
                traceback.print_exc()
                if caller:
                    caller.msg(ostring)

            current_obj_keys.add(obj_key)

    # Create new objects.
    object_model_name = ELEMENT("OBJECT").model_name
    for record in objects_data:
        if not record.key in current_obj_keys:
            # Create new objects.
            ostring = "Creating %s." % record.key
            print(ostring)
            if caller:
                caller.msg(ostring)

            try:
                object_record = WorldData.get_table_data(object_model_name, key=record.key)
                object_record = object_record[0]
                class_path = ELEMENT_SET.get_module(object_record.element_type)
                obj = create.create_object(class_path, object_record.name)
                count_create += 1
            except Exception as e:
                ostring = "Can not create obj %s: %s" % (record.key, e)
                print(ostring)
                traceback.print_exc()
                if caller:
                    caller.msg(ostring)
                continue

            try:
                obj.set_object_key(record.key, unique_type=type_name)
            except Exception as e:
                ostring = "Can not set data info to obj %s: %s" % (record.key, e)
                print(ostring)
                traceback.print_exc()
                if caller:
                    caller.msg(ostring)
                continue

    ostring = "Removed %d object(s). Created %d object(s). Updated %d object(s). Total %d objects.\n"\
              % (count_remove, count_create, count_update, len(objects_data))
    print(ostring)
    if caller:
        caller.msg(ostring)


def build_all(caller=None):
    """
    Build all objects in the world.

    Args:
        caller: (command caller) If provide, running messages will send to the caller.
    """
    # Build areas.
    build_unique_objects(WorldAreas.all(), "world_areas", caller)
    
    # Build rooms.
    build_unique_objects(WorldRooms.all(), "world_rooms", caller)
    reset_default_locations()


def reset_default_locations():
    """
    Reset default home and start location, get new positions from
    settings.DEFAULT_HOME_KEY and settings.START_LOCATION_KEY. If they
    are empty, set them to to the first room in settings.WORLD_ROOMS.
    """
    # Set default home.
    default_home_key = GAME_SETTINGS.get("default_home_key")
    if not default_home_key:
        # If does not have the default_home_key, get the first room in WORLD_ROOMS.
        try:
            rooms = WorldRooms.all()
            if rooms:
                default_home_key = rooms[0].key
        except Exception as e:
            ostring = "Can not find default_home_key: %s" % e
            print(ostring)
            traceback.print_exc()

    if default_home_key:
        try:
            default_home = search.get_object_by_key(default_home_key)
            settings.DEFAULT_HOME = default_home.dbref
            print("settings.DEFAULT_HOME set to: %s" % settings.DEFAULT_HOME)
        except Exception as e:
            print("Can not find default_home %s: (%s)%s" % (default_home_key, type(e), e))

    # Set start location.
    start_location_key = GAME_SETTINGS.get("start_location_key")
    if not start_location_key:
        # If does not have the start_location_key, get the first room in WORLD_ROOMS
        try:
            rooms = WorldRooms.all()
            if rooms:
                start_location_key = rooms[0].key
        except Exception as e:
            ostring = "Can not find start_location_key: %s" % e
            print(ostring)
            traceback.print_exc()

    if start_location_key:
        # If get start_location_key.
        try:
            start_location = search.get_object_by_key(start_location_key)
            settings.START_LOCATION = start_location.dbref
            print("settings.START_LOCATION set to: %s" % settings.START_LOCATION)
        except Exception as e:
            print("Can not find start_location: %s" % e)


def delete_object(obj_id):
    # helper function for deleting a single object
    try:
        obj = search.get_object_by_id(obj_id)

        # do the deletion
        okay = obj.delete()
        if not okay:
            ostring = "Can not delete %s." % obj_id
            print(ostring)
    except ObjectDoesNotExist:
        ostring = "Can not find object %s." % obj_id
        print(ostring)
    except Exception as e:
        ostring = "Can not delete object %s: %s %s." % (obj_id, type(e), e)
        print(ostring)


def create_player(playername, password, permissions=None, typeclass=None):
    """
    Helper function, creates a player of the specified typeclass.
    """
    if not permissions:
        permissions = settings.PERMISSION_ACCOUNT_DEFAULT

    new_player = create.create_account(playername, None, password,
                                       permissions=permissions, typeclass=typeclass)

    # This needs to be set so the engine knows this player is
    # logging in for the first time. (so it knows to call the right
    # hooks during login later)
    new_player.db.FIRST_LOGIN = True

    # join the new player to the public channel
    pchannel = ChannelDB.objects.get_channel(settings.DEFAULT_CHANNELS[0]["key"])
    if not pchannel.connect(new_player):
        string = "New player '%s' could not connect to public channel!" % new_player.key
        logger.log_err(string)

    return new_player
    

def create_character(new_player, nickname, character_key=None,
                     level=1, element_type=None, location_key=None, home_key=None):
    """
    Helper function, creates a character based on a player's name.
    """
    if not character_key:
        character_key = GAME_SETTINGS.get("default_player_character_key")

    if not element_type:
        element_type = settings.PLAYER_CHARACTER_ELEMENT_TYPE

    new_character = ELEMENT(element_type)()

    # set player's account id
    new_character.set_account_id(new_player.id)

    # Get a new player character id.
    char_db_id = SystemData.load("last_player_character_id", 0)
    char_db_id += 1
    SystemData.save("last_player_character_id", char_db_id)
    new_character.set_db_id(char_db_id)

    # set location
    if not location_key:
        location_key = GAME_SETTINGS.get("start_location_key")
        if not location_key:
            location_key = GAME_SETTINGS.get("default_player_home_key")
            if not location_key:
                location_key = settings.DEFAULT_HOME

    CharacterLocation.save(char_db_id, location_key)

    # Add nickname
    if not nickname:
        nickname = character_key

    # save data
    PlayerCharacter.add(new_player.id, char_db_id, nickname, level)

    # set nickname
    new_character.set_nickname(nickname)

    # set character info
    new_character.setup_element(character_key, level=level, first_time=True)

    return new_character

