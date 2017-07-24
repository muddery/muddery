"""
General helper functions that don't fit neatly under any given category.

They provide some useful string and conversion methods that might
be of use when designing your own game.

"""

from __future__ import print_function

import os
import re
from django.conf import settings
from evennia.utils import search, logger
from muddery.server.launcher import configs
from muddery.worlddata.data_sets import DATA_SETS


def get_muddery_version():
    """
    Get muddery's version.
    """
    import muddery
    return muddery.__version__


def set_obj_data_key(obj, key):
    """
    Set data key. Put it info into an object's attributes.
            
    Args:
        obj: (object) object to be set
        key: (string) key of the data.
    """
    obj.attributes.add("key", key, category=settings.DATA_KEY_CATEGORY, strattr=True)


def search_obj_data_key(key):
    """
    Search objects which have the given key.

    Args:
        key: (string) Data's key.
    """
    if not key:
        return None

    return search.search_object_attribute(key="key", strvalue=key, category=settings.DATA_KEY_CATEGORY)
    
    
def search_db_data_type(key, value, typeclass):
    """
    Search objects of the given typeclass which have the given value.
    """
    objs = search.search_object_attribute(key=key, value=value)
    return [obj for obj in objs if obj.is_typeclass(typeclass, exact=False)]


def set_obj_unique_type(obj, type):
    """
    Set unique object's type.

    Args:
        obj: (object) object to be set
        type: (string) unique object's type.
    """
    obj.attributes.add("type", type, category=settings.DATA_KEY_CATEGORY, strattr=True)


def search_obj_unique_type(type):
    """
    Search objects which have the given unique type.

    Args:
        type: (string) unique object's type.
    """
    obj = search.search_object_attribute(key="type", strvalue=type, category=settings.DATA_KEY_CATEGORY)
    return obj


def is_child(child, parent):
    """
    Check if the child class is inherited from the parent.

    Args:
        child: child class
        parent: parent class

    Returns:
        boolean
    """
    for base in child.__bases__:
        if base is parent:
            return True

    for base in child.__bases__:
        if is_child(base, parent):
            return True

    return False


def file_iterator(file, erase=False, chunk_size=512):
    while True:
        c = file.read(chunk_size)
        if c:
            yield c
        else:
            # remove temp file
            file.close()
            if erase:
                os.remove(file.name)
            break


def get_unlocalized_strings(filename, filter):
    """
    Get all unlocalized strings.

    Args:
        file_type: (string) type of file.
        filter: (boolean) filter exits strings or not.
        
    Returns:
        (set): a list of tuple (string, category).
    """
    re_func = re.compile(r'_\(\s*".+?\)')
    re_string = re.compile(r'".*?"')
    re_category = re.compile(r'category.*=.*".*?"')
    strings = set()
    
    # search in python files
    with open(filename, "r") as file:
        lines = file.readlines()
        for line in lines:
            # parse _() function
            for func in re_func.findall(line):
                str = ""
                cate = ""
                
                str_search = re_string.search(func)
                if str_search:
                    str = str_search.group()
                    #remove quotations
                    str = str[1:-1]
                    
                    cate_search = re_category.search(func)
                    if cate_search:
                        group = cate_search.group()
                        cate = re_string.search(group).group()
                        #remove quotations
                        cate = cate[1:-1] 

                if str or cate:
                    if filter:
                        # check database
                        records = DATA_SETS.localized_strings.objects.filter(category=cate,
                                                                             origin=str)
                        if not records:
                            strings.add((str, cate,))
                    else:
                        strings.add((str, cate,))
    return strings


def all_unlocalized_strings(file_type, filter):
    """
    Get all unlocalized strings.
    
    Args:
        file_type: (string) type of file.
        filter: (boolean) filter exits strings or not.

    Returns:
        (set): a list of tuple (string, category).
    """
    rootdir = configs.MUDDERY_LIB
    strings = set()
    ext = "." + file_type
    
    # get all _() args in all files
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext == ext:
                full_name = os.path.join(parent, filename)
                strings.update(get_unlocalized_strings(full_name, filter))
    return strings
                                




