"""
This module handles loading data from csv files and set data to objects.
"""

import ast
from django.db.models.loading import get_model
from django.conf import settings
from evennia.utils import search, logger
from muddery.utils.exception import MudderyError


################################################################
#
# These motherds set data to an object
#
################################################################

def set_obj_data_info(obj, model, key):
    """
    Set data_info's database. It saves info to attributes of data_info category, then load these data.

    Args:
        obj: Object in game.
        model: (string) Db model's name.
        key: (string) Key of the data info.
    """
    if not obj:
        return

    obj.attributes.add("model", model, category=settings.WORLD_DATA_INFO_CATEGORY, strattr=True)
    obj.attributes.add("key", key, category=settings.WORLD_DATA_INFO_CATEGORY, strattr=True)

    if (not model) or (not key):
        return

    load_data(obj)


def load_data(obj):
    """
    Load object data from db, and set them to the obj."

    Args:
        obj: Object in game.
    """
    if not obj:
        return

    # Get model and key names.
    model = obj.attributes.get(key="model", category=settings.WORLD_DATA_INFO_CATEGORY, strattr=True)
    if not model:
        return

    key = obj.attributes.get(key="key", category=settings.WORLD_DATA_INFO_CATEGORY, strattr=True)
    if not key:
        return

    # Get db model
    model_obj = get_model(settings.WORLD_DATA_APP, model)
    if not model_obj:
        raise MudderyError("%s can not open model %s" % (key, model))

    # Get data record.
    data_info = model_obj.objects.filter(key=key)
    if not data_info:
        raise MudderyError("%s can not find key %s" % (key, key))

    info = data_info[0]

    set_obj_typeclass(obj, info.typeclass)
    set_obj_name(obj, info.name)
    set_obj_alias(obj, info.alias)
    set_obj_location(obj, info.location)
    set_obj_home(obj, info.home)
    set_obj_desc(obj, info.desc)
    set_obj_lock(obj, info.lock)
    set_obj_destination(obj, info.destination)

    # Set attributes.
    attributes = {}
    if info.attributes:
        try:
            # info.attributes: (string) Attribues in form of python dict. Such as: "{'age':'22', 'career':'warrior'}"
            # Convert string to dict
            attributes = ast.literal_eval(info.attributes)
        except Exception, e:
            logger.log_errmsg("%s can't load attributes %s: %s" % (get_info_key(obj), info.attributes, e))

    # Add other fields to attributes.
    known_fields = {"key",
                    "name",
                    "alias",
                    "typeclass",
                    "location",
                    "home",
                    "desc",
                    "lock",
                    "destination",
                    "attributes"}

    for field in model_obj._meta.fields:
        if not field.name in known_fields:
            attributes[field.name] = info.serializable_value(field.name)

    set_obj_attributes(obj, attributes)
    return


def set_obj_typeclass(obj, typeclass):
    """
    Set object's typeclass.

    Args:
        obj: Object in game.
        typeclass: (string) Typeclass's name.
    """
    if not obj:
        return

    if not typeclass:
        typeclass = settings.BASE_OBJECT_TYPECLASS

    if obj.is_typeclass(typeclass, exact=True):
        # No change.
        return

    if not hasattr(obj, 'swap_typeclass'):
        logger.log_errmsg("%s cannot have a type at all!" % get_info_key(obj))
        return

    obj.swap_typeclass(typeclass, clean_attributes=False)



def set_obj_name(obj, name):
    """
    Set object's name.

    Args:
        obj: Object in game.
        name: (string) Name of the object.
    """
    if name == obj.name:
        # No change.
        return

    obj.name = name

    # we need to trigger this here, since this will force
    # (default) Exits to rebuild their Exit commands with the new
    # aliases
    #obj.at_cmdset_get(force_init=True)

    if obj.destination:
        obj.flush_from_cache()


def set_obj_alias(obj, aliases):
    """
    Set object's alias.

    Args:
        obj: Object in game.
        aliases: (string) Aliases of the object.
    """
    # merge the old and new aliases (if any)
    new_aliases = [alias.strip().lower() for alias in aliases.split(';')
                   if alias.strip()]

    set_new_aliases = set(new_aliases)
    set_current_aliases = set(obj.aliases.all())

    if set_new_aliases == set_current_aliases:
        # No change.
        return

    obj.aliases.clear()
    obj.aliases.add(new_aliases)

    # we need to trigger this here, since this will force
    # (default) Exits to rebuild their Exit commands with the new
    # aliases
    #obj.at_cmdset_get(force_init=True)

    if obj.destination:
        obj.flush_from_cache()


def set_obj_location(obj, location):
    """
    Set object's location.

    Args:
        obj: Object in game.
        location: (string) Location's name. Must be the key of data info.
    """
    location_obj = None

    if location:
        # If has location, search location object.
        location_obj = search_obj_info_key(location)

        if not location_obj:
            logger.log_errmsg("%s can't find location %s!" % (get_info_key(obj), location))
            return

        location_obj = location_obj[0]

    if obj.location == location_obj:
        # No change.
        return

    if obj == location_obj:
        # Can't set location to itself.
        logger.log_errmsg("%s can't teleport itself to itself!" % get_info_key(obj))
        return

    # try the teleport
    obj.move_to(location_obj, quiet=True, to_none=True)


def set_obj_home(obj, home):
    """
    Set object's home.

    Args:
        obj: Object in game.
        home: (string) Home's name. Must be the key of data info.
    """
    home_obj = None

    if home:
        # If has home, search home object.
        home_obj = search_obj_info_key(home)

        if not home_obj:
            logger.log_errmsg("%s can't find home %s!" % (get_info_key(obj), home))
            return

        home_obj = home_obj[0]

    if obj.home == home_obj:
        # No change.
        return

    if obj == home_obj:
        # Can't set home to itself.
        logger.log_errmsg("%s can't set home to itself!" % get_info_key(obj))
        return

    obj.home = home_obj


def set_obj_desc(obj, desc):
    """
    Set object's description.

    Args:
        obj: Object in game.
        desc: (string) Description.
    """
    obj.db.desc = desc


def set_obj_lock(obj, lock):
    """
    Set object's lock.

    Args:
        obj: Object in game.
        lock: (string) Object's lock string.
    """
    if lock:
        try:
            obj.locks.add(lock)
        except Exception:
            logger.log_errmsg("%s can't set lock %s." % (get_info_key(obj), lock))


def set_obj_attributes(obj, attributes):
    """
    Set object's attribute.

    Args:
        obj: Object in game.
        attributes: (dict) Object's attribues."
    """
    if not attributes:
        return

    for key in attributes:
        # Add attributes.
        try:
            obj.attributes.add(key, attributes[key])
        except Exception:
            logger.log_errmsg("%s can't set attribute %s!" % (get_info_key(obj), key))


def set_obj_destination(obj, destination):
    """
    Set object's destination

    Args:
        obj: Object in game.
        destination: (string) Destination's name. Must be the key of data info.
    """
    destination_obj = None

    if destination:
        # If has destination, search destination object.
        destination_obj = search_obj_info_key(destination)

        if not destination_obj:
            logger.log_errmsg("%s can't find destination %s!" % (get_info_key(obj), destination))
            return

        destination_obj = destination_obj[0]

    if obj.destination == destination_obj:
        # No change.
        return

    if obj == destination_obj:
        # Can't set destination to itself.
        logger.log_errmsg("%s can't set destination to itself!" % get_info_key(obj))
        return

    obj.destination = destination_obj


def set_obj_detail(obj, key, detail):
    """
    Set object's detail.

    Args:
        obj: Object in game.
        key: (string) Detail's key.
        detail: (string) Detail's info.
    """
    if hasattr(obj, "set_detail"):
        obj.set_detail(key, detail)


def get_info_key(obj):
    """
    Get an object's data info key.

    Args:
        obj: Object in game.
    """
    return obj.attributes.get(key="key", category=settings.WORLD_DATA_INFO_CATEGORY, strattr=True)


def search_obj_info_key(key):
    """
    Search objects which have the given key.

    Args:
        key: (string) Data info key.
    """
    obj = search.search_object_attribute(key="key", strvalue=key, category=settings.WORLD_DATA_INFO_CATEGORY)
    return obj


def search_obj_info_model(model):
    """
    Search objects which have the given model.

    Args:
        model: (string) Data model's name.
    """
    obj = search.search_object_attribute(key="model", strvalue=model, category=settings.WORLD_DATA_INFO_CATEGORY)
    return obj
