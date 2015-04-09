"""
This module handles importing data from csv files and creating the whole game world from these data.
"""

import os
import django
import loader
from django.conf import settings
from django.db.models.loading import get_model
from evennia.utils import create, search, logger


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
    if caller:
        caller.msg("Building %s." % model_name)

    model_obj = get_model(settings.WORLD_DATA_APP, model_name)
    
    # new objects
    new_obj_names = set(record.key for record in model_obj.objects.all())

    # current objects
    current_objs = loader.search_obj_info_model(model_name)

    # remove objects
    count_remove = 0
    count_create = 0
    current_obj_keys = set()
    
    for obj in current_objs:
        obj_key = loader.get_info_key(obj)
        
        if unique:
            if obj_key in current_obj_keys:
                # This object is duplcated.
                if caller:
                    caller.msg("Deleting %s" % obj_key)
                obj.delete()
                count_remove += 1
                continue
                
            if not obj_key in new_obj_names:
                # This object should be removed
                if caller:
                    caller.msg("Deleting %s" % obj_key)
                obj.delete()
                count_remove += 1
                continue
        
        # Refresh object.
        loader.load_data(obj)
        if caller:
            caller.msg("%s updated." % obj_key)
        
        current_obj_keys.add(obj_key)

    if unique:
        # Create objects.
        for record in model_obj.objects.all():
            if not record.key in current_obj_keys:
                # Create new objects.
                obj = create.create_object(record.typeclass,
                                           record.name)
                loader.set_obj_data_info(obj, model_name, record.key)
                count_create += 1

                if caller:
                    caller.msg("%s created." % record.key)

    if caller:
        string = "Removed %d object(s). Created %d object(s). Total %d objects.\n" % (count_remove, count_create, len(model_obj.objects.all()))
        caller.msg(string)


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
        location_objs = loader.search_obj_info_key(record.location)
        
        # Detail's location.
        for location in location_objs:
            loader.set_obj_detail(location, record.name, record.desc);

            for name in record.name.split(";"):
                loader.set_obj_detail(location, name, record.desc);
                
            count += 1

    if caller:
        string = "Set %d detail(s)." % count
        caller.msg(string)


def build_all(caller=None):
    """
    Load csv data and build the world.
    
    Args:
        caller: (command caller) If provide, running messages will send to the caller.
    """

    for room in settings.WORLD_ROOMS:
        build_objects(room, True, caller)

    for exit in settings.WORLD_EXITS:
        build_objects(exit, True, caller)

    for object in settings.WORLD_OBJECTS:
        build_objects(object, True, caller)

    for object in settings.PERSONAL_OBJECTS:
        build_objects(object, False, caller)

    for detail in settings.WORLD_DETAILS:
        build_details(detail, caller)


