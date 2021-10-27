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

from muddery.server.utils.game_settings import GAME_SETTINGS
import traceback

LIMBO_DESC = "Welcome to your new {wMuddery{n-based game! " +\
             "Visit http://www.muddery.org if you need help, " +\
             "want to contribute, report issues or just join the community."


def at_initial_setup():
    """
    Build up the default world and set default locations.
    """

    try:
        # load data
        from muddery.server.database.worlddata.worlddata import WorldData
        WorldData.reload()
        print("Reload world data.")

        # load game settings
        GAME_SETTINGS.reset()
        print("Reset game settings.")

    except Exception as e:
        ostring = "Can't set initial data: %s" % e
        print(ostring)
        print(traceback.format_exc())
