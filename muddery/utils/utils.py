"""
General helper functions that don't fit neatly under any given category.

They provide some useful string and conversion methods that might
be of use when designing your own game.

"""

import os
from evennia.utils import logger


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
