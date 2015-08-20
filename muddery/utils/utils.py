"""
General helper functions that don't fit neatly under any given category.

They provide some useful string and conversion methods that might
be of use when designing your own game.

"""

import os
from django.conf import settings
from evennia.utils import search, logger


def get_muddery_version():
    """
    Get muddery's version.
    """
    import muddery
    return muddery.__version__


def copy_tree(source, destination):
    names = os.listdir(source)

    if not os.path.exists(destination):
        # If does not exist, create one.
        os.mkdir(destination)

    # traverse files and folders
    for name in names:
        srcname = os.path.join(source, name)
        dstname = os.path.join(destination, name)
        try:
            if os.path.isdir(srcname):
                # If it is a folder, copy it recursively.
                copy_tree(srcname, dstname)
            else:
                # Copy file.
                shutil.copy2(srcname, dst)
        except Exception, e:
            logger.log_errmsg("Can not copy file:%s to %s" % (srcname, dstname))


def set_obj_data_info(obj, key):
    """
    Set data_info's model and key. It puts info into attributes.
            
    Args:
        model: (string) Db model's name.
        key: (string) Key of the data info.
    """
    obj.attributes.add("key", key, category=settings.WORLD_DATA_INFO_CATEGORY, strattr=True)


def search_obj_info_key(key):
    """
    Search objects which have the given key.

    Args:
    key: (string) Data info key.
    """
    if not key:
        return None

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
