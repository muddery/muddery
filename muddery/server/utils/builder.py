"""
This module handles importing data from csv files and creating the whole game world from these data.
"""

import traceback
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils import create, search, logger
from evennia.comms.models import ChannelDB
from muddery.server.utils import utils
from muddery.server.utils.game_settings import GAME_SETTINGS
from muddery.server.mappings.element_set import ELEMENT, ELEMENT_SET
from muddery.server.database.gamedata.object_keys import OBJECT_KEYS
from muddery.server.database.worlddata.worlddata import WorldData
from muddery.server.database.worlddata.world_areas import WorldAreas
from muddery.server.database.worlddata.world_rooms import WorldRooms
from muddery.server.database.worlddata.world_exits import WorldExits
from muddery.server.database.worlddata.world_npcs import WorldNPCs
from muddery.server.database.worlddata.world_objects import WorldObjects


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
        print(traceback.print_exc())

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
            print(traceback.print_exc())

        # get element model
        class_path = ELEMENT_SET.get_module(record.element_type)
    except Exception as e:
        ostring = "Can not get the element type of %s: %s." % (obj_key, e)
        print(ostring)
        print(traceback.print_exc())
        pass

    if not record or not class_path:
        ostring = "Can not find the data of %s." % obj_key
        print(ostring)
        print(traceback.print_exc())
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
        print(traceback.print_exc())
        if caller:
            caller.msg(ostring)
        return

    try:
        # Set data info.
        obj.set_object_key(record.key, level, reset_location=reset_location)
        obj.after_creation()
    except Exception as e:
        ostring = "Can not set data info to obj %s: %s" % (obj_key, e)
        print(ostring)
        print(traceback.print_exc())
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
            obj = utils.get_object_by_id(obj_id)
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
                ostring = "%s can not load data:%s" % (obj.dbref, e)
                print(ostring)
                print(traceback.print_exc())
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
                print(traceback.print_exc())
                if caller:
                    caller.msg(ostring)
                continue

            try:
                obj.set_object_key(record.key, type_name)
                obj.after_creation()
            except Exception as e:
                ostring = "Can not set data info to obj %s: %s" % (record.key, e)
                print(ostring)
                print(traceback.print_exc())
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

    # Build exits.
    build_unique_objects(WorldExits.all(), "world_exits", caller)

    # Build objects.
    build_unique_objects(WorldObjects.all(), "world_objects", caller)

    # Build NPCs.
    build_unique_objects(WorldNPCs.all(), "world_npcs", caller)


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
            print(traceback.print_exc())

    if default_home_key:
        try:
            default_home = utils.get_object_by_key(default_home_key)
            settings.DEFAULT_HOME = default_home.dbref
            print("settings.DEFAULT_HOME set to: %s" % settings.DEFAULT_HOME)
        except Exception as e:
            print("Can not find default_home: %s" % e)

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
            print(traceback.print_exc())

    if start_location_key:
        # If get start_location_key.
        try:
            start_location = utils.get_object_by_key(start_location_key)
            settings.START_LOCATION = start_location.dbref
            print("settings.START_LOCATION set to: %s" % settings.START_LOCATION)
        except Exception as e:
            print("Can not find start_location: %s" % e)


def delete_object(obj_dbref):
    # helper function for deleting a single object
    obj = search.search_object(obj_dbref)
    if not obj:
        ostring = "Can not find object %s." % obj_dbref
        print(ostring)

    # do the deletion
    okay = obj[0].delete()
    if not okay:
        ostring = "Can not delete %s." % obj_dbref
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
    

def create_character(new_player, nickname, permissions=None, character_key=None,
                     level=1, typeclass=None, location=None, home=None):
    """
    Helper function, creates a character based on a player's name.
    """
    if not character_key:
        character_key = GAME_SETTINGS.get("default_player_character_key")

    if not typeclass:
        typeclass = settings.BASE_PLAYER_CHARACTER_TYPECLASS
        
    if not permissions:
        permissions = settings.PERMISSION_ACCOUNT_DEFAULT
    
    if not home:
        default_home_key = GAME_SETTINGS.get("default_player_home_key")
        if default_home_key:
            try:
                home = utils.get_object_by_key(default_home_key)
            except ObjectDoesNotExist:
                pass

    if not home:
        rooms = search.search_object(settings.DEFAULT_HOME)
        if rooms:
            home = rooms[0]

    if not location:
        location = home
        try:
            start_location_key = GAME_SETTINGS.get("start_location_key")
            if start_location_key:
                location = utils.get_object_by_key(start_location_key)
        except:
            pass

    new_character = create.create_object(typeclass, key=new_player.key, location=location,
                                         home=home, permissions=permissions)

    # set character info
    new_character.set_object_key(character_key, level)
    new_character.after_creation()

    # set playable character list
    new_player.db._playable_characters.append(new_character)

    # allow only the character itself and the player to puppet this character (and Immortals).
    new_character.locks.add("puppet:id(%i) or pid(%i) or perm(Immortals) or pperm(Immortals)" %
                            (new_character.id, new_player.id))

    # If no description is set, set a default description
    if not new_character.db.desc:
        new_character.db.desc = "This is a Player."

    # Add nickname
    if not nickname:
        nickname = character_key
    new_character.set_nickname(nickname)
        
    # We need to set this to have @ic auto-connect to this character
    new_player.db._last_puppet = new_character
    
    return new_character

