"""
This module handles importing data from csv files and creating the whole game world from these data.
"""

from __future__ import print_function

from muddery.utils import utils
from muddery.utils.object_key_handler import OBJECT_KEY_HANDLER
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.mappings.typeclass_set import TYPECLASS_SET
from muddery.worlddata.dao import common_mappers as CM
from django.conf import settings
from django.apps import apps
from evennia.utils import create, search, logger
from evennia.comms.models import ChannelDB
import traceback


def get_object_record(obj_key):
    """
    Query the object's record.

    Args:
        obj_key: (string) The key of the object.

    Returns:
        The object's data record.
    """
    record = None
    model_names = OBJECT_KEY_HANDLER.get_models(obj_key)
    for model_name in model_names:
        try:
            # Get record.
            model_obj = apps.get_model(settings.WORLD_DATA_APP, model_name)
            record = model_obj.objects.get(key=obj_key)
            break
        except Exception, e:
            ostring = "Can not get record %s: %s." % (obj_key, e)
            print(ostring)
            print(traceback.print_exc())
            continue

    return record


def build_object(obj_key, caller=None, set_location=True):
    """
    Build objects of a model.

    Args:
        obj_key: (string) The key of the object.
        caller: (command caller) If provide, running messages will send to the caller.
    """

    # Get object's information
    record = None
    typeclass_path = None
    try:
        record = get_object_record(obj_key)

        # get typeclass model
        typeclass_path = TYPECLASS_SET.get_module(record.typeclass)
    except Exception, e:
        ostring = "Can not get typeclass of %s: %s." % (obj_key, e)
        print(ostring)
        print(traceback.print_exc())
        pass

    if not record or not typeclass_path:
        ostring = "Can not find the data of %s." % obj_key
        print(ostring)
        print(traceback.print_exc())
        if caller:
            caller.msg(ostring)
        return

    # Create object.
    try:
        name = getattr(record, "name", "")
        obj = create.create_object(typeclass_path, name)
    except Exception, e:
        ostring = "Can not create obj %s: %s" % (obj_key, e)
        print(ostring)
        print(traceback.print_exc())
        if caller:
            caller.msg(ostring)
        return

    try:
        # Set data info.
        obj.set_data_key(record.key, set_location=set_location)
    except Exception, e:
        ostring = "Can not set data info to obj %s: %s" % (obj_key, e)
        print(ostring)
        print(traceback.print_exc())
        if caller:
            caller.msg(ostring)
        return

    if record.typeclass == settings.TWO_WAY_EXIT_TYPECLASS_KEY:
        # If it's a two way exit, create the reverse exit.

        # Create object.
        try:
            obj = create.create_object(TYPECLASS_SET.get_module(settings.REVERSE_EXIT_TYPECLASS_KEY), record.name)
        except Exception, e:
            ostring = "Can not create obj %s: %s" % (obj_key, e)
            print(ostring)
            print(traceback.print_exc())
            if caller:
                caller.msg(ostring)
            return

        try:
            # Set data info.
            obj.set_data_key(settings.REVERSE_EXIT_PREFIX + record.key)
        except Exception, e:
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

    # reverse exits
    reverse_exits = set(settings.REVERSE_EXIT_PREFIX + record.key
                        for record in objects_data
                            if record.typeclass==settings.TWO_WAY_EXIT_TYPECLASS_KEY)

    new_obj_keys.update(reverse_exits)

    # current objects
    current_objs = utils.search_obj_unique_type(type_name)

    # remove objects
    count_remove = 0
    count_update = 0
    count_create = 0
    current_obj_keys = set()

    for obj in current_objs:
        obj_key = obj.get_data_key()

        if obj_key in current_obj_keys:
            # This object is duplcated.
            ostring = "Deleting %s" % obj_key
            print(ostring)
            if caller:
                caller.msg(ostring)

            obj.delete()
            count_remove += 1
            continue

        if not obj_key in new_obj_keys:
            # This object should be removed
            ostring = "Deleting %s" % obj_key
            print(ostring)
            if caller:
                caller.msg(ostring)

            obj.delete()
            count_remove += 1
            continue

        try:
            # set data
            obj.load_data()
            # put obj to its default location
            obj.reset_location()
        except Exception, e:
            ostring = "%s can not load data:%s" % (obj.dbref, e)
            print(ostring)
            print(traceback.print_exc())
            if caller:
                caller.msg(ostring)

        current_obj_keys.add(obj_key)

    # Create new objects.
    for record in objects_data:
        if not record.key in current_obj_keys:
            # Create new objects.
            ostring = "Creating %s." % record.key
            print(ostring)
            if caller:
                caller.msg(ostring)

            try:
                typeclass_path = TYPECLASS_SET.get_module(record.typeclass)
                obj = create.create_object(typeclass_path, record.name)
                count_create += 1
            except Exception, e:
                ostring = "Can not create obj %s: %s" % (record.key, e)
                print(ostring)
                print(traceback.print_exc())
                if caller:
                    caller.msg(ostring)
                continue

            try:
                obj.set_data_key(record.key)
                utils.set_obj_unique_type(obj, type_name)
            except Exception, e:
                ostring = "Can not set data info to obj %s: %s" % (record.key, e)
                print(ostring)
                print(traceback.print_exc())
                if caller:
                    caller.msg(ostring)
                continue

        if record.typeclass == settings.TWO_WAY_EXIT_TYPECLASS_KEY:
            # If it's a two way exit, create the reverse exit.
            reverse_exit_key = settings.REVERSE_EXIT_PREFIX + record.key
            if not reverse_exit_key in current_obj_keys:
                ostring = "Creating %s." % reverse_exit_key
                print(ostring)
                if caller:
                    caller.msg(ostring)

                # Create object.
                try:
                    typeclass_path = TYPECLASS_SET.get_module(settings.REVERSE_EXIT_TYPECLASS_KEY)
                    obj = create.create_object(typeclass_path, record.name)
                    count_create += 1
                except Exception, e:
                    ostring = "Can not create obj %s: %s" % (reverse_exit_key, e)
                    print(ostring)
                    print(traceback.print_exc())
                    if caller:
                        caller.msg(ostring)
                    return

                try:
                    # Set data info.
                    obj.set_data_key(reverse_exit_key)
                    utils.set_obj_unique_type(obj, type_name)
                except Exception, e:
                    ostring = "Can not set data info to obj %s: %s" % (reverse_exit_key, e)
                    print(ostring)
                    print(traceback.print_exc())
                    if caller:
                        caller.msg(ostring)
                    return

    ostring = "Removed %d object(s). Created %d object(s). Updated %d object(s). Total %d objects.\n"\
              % (count_remove, count_create, count_update, len(objects_data) + len(reverse_exits))
    print(ostring)
    if caller:
        caller.msg(ostring)


def build_all(caller=None):
    """
    Build all objects in the world.

    Args:
        caller: (command caller) If provide, running messages will send to the caller.
    """
    print("build_all")

    # Reset object key's info.
    OBJECT_KEY_HANDLER.reload()

    # Build areas.
    build_unique_objects(CM.WORLD_AREAS.all(), "world_areas", caller)
    
    # Build rooms.
    build_unique_objects(CM.WORLD_ROOMS.all(), "world_rooms", caller)

    # Build exits.
    build_unique_objects(CM.WORLD_EXITS.all(), "world_exits", caller)

    # Build objects.
    build_unique_objects(CM.WORLD_OBJECTS.all(), "world_objects", caller)

    # Build NPCs.
    build_unique_objects(CM.WORLD_NPCS.all(), "world_npcs", caller)


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
            rooms = CM.WORLD_ROOMS.all()
            if rooms:
                default_home_key = rooms[0].key
        except Exception, e:
            ostring = "Can not find default_home_key: %s" % e
            print(ostring)
            print(traceback.print_exc())

    if default_home_key:
        # If get default_home_key.
        default_home = utils.search_obj_data_key(default_home_key)
        if default_home:
            # Set default home.
            settings.DEFAULT_HOME = default_home[0].dbref
            print("settings.DEFAULT_HOME set to: %s" % settings.DEFAULT_HOME)
    
    # Set start location.
    start_location_key = GAME_SETTINGS.get("start_location_key")
    if not start_location_key:
        # If does not have the start_location_key, get the first room in WORLD_ROOMS
        try:
            rooms = CM.WORLD_ROOMS.all()
            if rooms:
                start_location_key = rooms[0].key
        except Exception, e:
            ostring = "Can not find start_location_key: %s" % e
            print(ostring)
            print(traceback.print_exc())

    if start_location_key:
        # If get start_location_key.
        start_location = utils.search_obj_data_key(start_location_key)
        if start_location:
            settings.START_LOCATION = start_location[0].dbref
            print("settings.START_LOCATION set to: %s" % settings.START_LOCATION)


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
        home = settings.DEFAULT_HOME
        try:
            default_home_key = GAME_SETTINGS.get("default_player_home_key")
            if default_home_key:
                rooms = utils.search_obj_data_key(default_home_key)
                home = rooms[0]
        except:
            pass
                        
    if not location:
        location = home
        try:
            start_location_key = GAME_SETTINGS.get("start_location_key")
            if start_location_key:
                rooms = utils.search_obj_data_key(start_location_key)
                location = rooms[0]
        except:
            pass

    new_character = create.create_object(typeclass, key=new_player.key, location=location,
                                         home=home, permissions=permissions)

    # set character info
    new_character.set_data_key(character_key)
    new_character.set_level(level)

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

