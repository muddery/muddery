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

from __future__ import print_function

import os
from django.conf import settings
from evennia.utils import search, logger
from muddery.utils import builder, importer, utils
from muddery.utils.game_settings import GAME_SETTINGS
from muddery.worlddata.data_sets import DATA_SETS
from muddery.typeclasses.character_skills import MudderySkill
import traceback

LIMBO_DESC = "Welcome to your new {wMuddery{n-based game! " +\
             "Visit http://www.muddery.org if you need help, " +\
             "want to contribute, report issues or just join the community."

def at_initial_setup():
    """
    Build up the default world and set default locations.
    """

    try:
        # load world data
        import_local_data()
        print("Import local data.")

        # load game settings
        GAME_SETTINGS.reset()
        print("Reset game settings.")

        # build world
        builder.build_all()
        print("Builder build all.")

        # set limbo's desc
        limbo_obj = search.search_object("#2", exact=True)
        if limbo_obj:
            limbo_obj[0].db.desc = LIMBO_DESC
            limbo_obj[0].position = None
        print("Set limbo object.")

        # set default locations
        builder.reset_default_locations()
        print("Set default locations.")

        superuser = search.search_object("#1", exact=True)
        if superuser:
            superuser = superuser[0]

            # move the superuser to the start location
            start_location = search.search_object(settings.START_LOCATION, exact=True)
            if start_location:
                start_location = start_location[0]
                superuser.move_to(start_location, quiet=True)

            # set superuser's data
            superuser.set_data_key(GAME_SETTINGS.get("default_player_character_key"))
            superuser.set_level(1)
            superuser.set_nickname("superuser")
            print("Set supervisor.")

    except Exception, e:
        ostring = "Can't set initial data: %s" % e
        print(ostring)
        print(traceback.format_exc())


def import_local_data():
    """
    Import all local data files to models.
    """
    ##########################
    # load system data
    ##########################
    # system data file's path
    system_data_path = os.path.join(settings.MUDDERY_DIR, settings.WORLD_DATA_FOLDER)

    # load system data
    for data_handlers in DATA_SETS.system_data:
        try:
            data_handlers.import_from_path(system_data_path, system_data=True)
        except Exception, e:
            err_message = "Cannot import game data. %s" % e
            logger.log_tracemsg(err_message)

    ##########################
    # load custom data
    ##########################
    # custom data file's path
    custom_data_path = os.path.join(settings.GAME_DIR, settings.WORLD_DATA_FOLDER)

    # load all custom data
    for data_handlers in DATA_SETS.all_handlers:
        try:
            data_handlers.import_from_path(custom_data_path, system_data=False)
        except Exception, e:
            err_message = "Cannot import game data. %s" % e
            logger.log_tracemsg(err_message)
