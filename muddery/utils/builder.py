"""
This module handles importing data from csv files and creating the whole game world from these data.
"""

from muddery.utils import utils
from muddery.utils.object_key_handler import OBJECT_KEY_HANDLER
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import create, search


def build_object(model_name, object_key, caller=None):
    """
    Build objects of a model.

    Args:
        model_name: (string) The name of the data model.
        obj_key: (string) The key of the object.
        caller: (command caller) If provide, running messages will send to the caller.
    """
    try:
        model_obj = get_model(settings.WORLD_DATA_APP, model_name)
        record = model_obj.objects.filter(key=object_key)
        record = record[0]
    except Exception, e:
        ostring = "Can not load record %s:%s %s" % (model_name, obj_key, e)
        print ostring
        return
    
    # Create object.
    try:
        obj = create.create_object(record.typeclass, record.name)
    except Exception, e:
        ostring = "Can not create obj %s: %s" % (record.name, e)
        print ostring
        if caller:
            caller.msg(ostring)
        return

    try:
        obj.set_data_info(model_name, record.key)
        obj.load_data()
    except Exception, e:
        ostring = "Can not set data info to obj %s: %s" % (record.name, e)
        print ostring
        if caller:
            caller.msg(ostring)
        return

    return obj


def build_objects(model_name, unique, caller=None):
    """
    Build objects of a model.

    Args:
        model_name: (string) The name of the data model.
        unique: (boolean) If unique, every record in model should has one and only one
                          object in the world.
                          If not unique, a record can has zero or multiple objects.
        caller: (command caller) If provide, running messages will send to the caller.
    """
    ostring = "Building %s." % model_name
    print ostring
    if caller:
        caller.msg(ostring)

    model_obj = get_model(settings.WORLD_DATA_APP, model_name)

    # new objects
    new_obj_names = set(record.key for record in model_obj.objects.all())

    # current objects
    current_objs = utils.search_obj_info_model(model_name)

    # remove objects
    count_remove = 0
    count_update = 0
    count_create = 0
    current_obj_keys = set()

    for obj in current_objs:
        obj_key = obj.get_info_key()

        if unique:
            if obj_key in current_obj_keys:
                # This object is duplcated.
                ostring = "Deleting %s" % obj_key
                print ostring
                if caller:
                    caller.msg(ostring)

                obj.delete()
                count_remove += 1
                continue

            if not obj_key in new_obj_names:
                # This object should be removed
                ostring = "Deleting %s" % obj_key
                print ostring
                if caller:
                    caller.msg(ostring)

                obj.delete()
                count_remove += 1
                continue

        try:
            obj.load_data()
        except Exception, e:
            print "%s can not load data:%s" % (obj.dbref, e)

        current_obj_keys.add(obj_key)

    if unique:
        # Create objects.
        for record in model_obj.objects.all():
            if not record.key in current_obj_keys:
                # Create new objects.
                ostring = "Creating %s." % record.key
                print ostring
                if caller:
                    caller.msg(ostring)

                try:
                    obj = create.create_object(record.typeclass, record.name)
                    count_create += 1
                except Exception, e:
                    ostring = "Can not create obj %s: %s" % (record.name, e)
                    print ostring
                    if caller:
                        caller.msg(ostring)
                    continue

                try:
                    obj.set_data_info(model_name, record.key)
                    obj.load_data()
                except Exception, e:
                    ostring = "Can not set data info to obj %s: %s" % (record.name, e)
                    print ostring
                    if caller:
                        caller.msg(ostring)
                    continue

    ostring = "Removed %d object(s). Created %d object(s). Updated %d object(s). Total %d objects.\n"\
              % (count_remove, count_create, count_update, len(model_obj.objects.all()))
    print ostring
    if caller:
        caller.msg(ostring)


def build_details(model_name, caller=None):
    """
    Build details of a model.

    Args:
        model_name: (string) The name of the data model.
        caller: (command caller) If provide, running messages will send to the caller.
    """

    model_detail = get_model(settings.WORLD_DATA_APP, model_name)

    # Remove all details
    objects = search.search_object_attribute(key="details")
    for obj in objects:
        obj.attributes.remove("details")

    # Set details.
    count = 0
    for record in model_detail.objects.all():
        location_objs = utils.search_obj_info_key(record.location)

        # Detail's location.
        for location in location_objs:
            for name in record.name.split(";"):
                location.set_detail(name, record.desc)

            count += 1

    ostring = "Set %d detail(s)." % count
    print ostring
    if caller:
        caller.msg(ostring)


def build_all(caller=None):
    """
    Load csv data and build the world.

    Args:
        caller: (command caller) If provide, running messages will send to the caller.
    """
    
    OBJECT_KEY_HANDLER.reload()

    for room_info in settings.WORLD_ROOMS:
        build_objects(room_info, True, caller)

    for exit_info in settings.WORLD_EXITS:
        build_objects(exit_info, True, caller)

    for object_info in settings.WORLD_OBJECTS:
        build_objects(object_info, True, caller)

    for npc_info in settings.WORLD_NPCS:
        build_objects(npc_info, True, caller)


def reset_default_locations():
    """
    Reset default home and start location, get new positions from
    settings.DEFAULT_HOME_KEY and settings.START_LOCATION_KEY. If they
    are empty, set them to to the first room in settings.WORLD_ROOMS.
    """

    # set default home
    default_home_key = settings.DEFAULT_HOME_KEY
    if not default_home_key:
        # get the first room in WORLD_ROOMS
        try:
            model_obj = get_model(settings.WORLD_DATA_APP, settings.WORLD_ROOMS[0])
            rooms = model_obj.objects.all()
            if rooms:
                default_home_key = rooms[0].key
        except Exception, e:
            ostring = "Can not find default_home_key: %s" % e
            print ostring

    if default_home_key:
        default_home = utils.search_obj_info_key(default_home_key)
        if default_home:
            settings.DEFAULT_HOME = default_home[0].dbref
            print "settings.DEFAULT_HOME set to: %s" % settings.DEFAULT_HOME

    # set start location
    start_location_key = settings.START_LOCATION_KEY
    if not start_location_key:
        # get the first room in WORLD_ROOMS
        try:
            model_obj = get_model(settings.WORLD_DATA_APP, settings.WORLD_ROOMS[0])
            rooms = model_obj.objects.all()
            if rooms:
                start_location_key = rooms[0].key
        except Exception, e:
            ostring = "Can not find start_location_key: %s" % e
            print ostring

    if start_location_key:
        start_location = utils.search_obj_info_key(start_location_key)
        if start_location:
            settings.START_LOCATION = start_location[0].dbref
            print "settings.START_LOCATION set to: %s" % settings.START_LOCATION
