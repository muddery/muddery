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

from evennia.utils import search, logger
from muddery.utils import builder, importer, utils

LIMBO_DESC = "Welcome to your new {wMuddery{n-based game! " +\
             "Visit http://www.muddery.org if you need help, " +\
             "want to contribute, report issues or just join the community."

def at_initial_setup():
    """
    When initiate the server, give an unique id to limbo and build up the default world.
    """

    # set data info to limbo
    limbo_obj = search.search_object("#2", exact=True)
    if limbo_obj:
        limbo_obj[0].db.desc = LIMBO_DESC
        try:
            utils.set_obj_data_info(limbo_obj[0], "world_rooms", "limbo")
        except Exception, e:
            logger.log_errmsg("Can't set data info to limbo: %s" % e)

    try:
        # load world data
        importer.import_all()

        # build world
        builder.build_all()
    except Exception, e:
        logger.log_errmsg("Can't build world: %s" % e)
