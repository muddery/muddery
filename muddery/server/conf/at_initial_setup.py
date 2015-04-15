"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""

from evennia.utils import search
from muddery.utils import loader

def at_initial_setup():
    # set datainfo to limbo
    limboobj = search.search_object("#2", exact=True)
    if limboobj:
        loader.set_obj_data_info(limboobj[0], "", "limbo")
